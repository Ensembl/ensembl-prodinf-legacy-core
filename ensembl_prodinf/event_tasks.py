'''
@author: dstaines; vinay
'''

import re
from ensembl_prodinf.event_celery_app import app
from ensembl_prodinf.event_client import EventClient
from sqlalchemy.engine.url import make_url
from ensembl_prodinf.event_client import QrpClient
#from ensembl.qrp.start_pipeline import RemoteCmd
from ensembl.production.workflow.monitor import RemoteCmd
from ensembl.production.workflow.hive import construct_pipeline
#from ensembl.qrp.util import construct_pipeline
from ensembl.qrp.payload import payload
from ensembl.qrp.es import PipelineStatus
from ensembl.production.workflow.dispatcher import WorkflowDispatcher


import event_config as cfg
from ensembl_prodinf import reporting
import json



species_pattern = re.compile(r'^(?P<prefix>\w+)_(?P<type>core|rnaseq|cdna|otherfeatures|variation|funcgen)(_\d+)?_(?P<release>\d+)_(?P<assembly>\d+)$')
compara_pattern = re.compile(r'^ensembl_compara(_(?P<division>[a-z]+|pan)(_homology)?)?(_(\d+))?(_\d+)$')
ancestral_pattern = re.compile(r'^ensembl_ancestral(_(?P<division>[a-z]+))?(_(\d+))?(_\d+)$')

event_client = EventClient(cfg.event_uri)
qrp_clinet = QrpClient(cfg.event_uri)

pool = reporting.get_pool(cfg.report_server)

def get_logger():
    """Obtain a logger from the reporting module that can write persistent reports"""
    return reporting.get_logger(pool, cfg.report_exchange, 'event_processing', None, {})

@app.task(bind=True)
def process_result(self, event, process, job_id):
    """
    Wait for the completion of the job and then process any output further
    """
    reporting.set_logger_context(get_logger(), event['genome'], event)

    # allow infinite retries
    self.max_retries = None
    get_logger().info("Checking {} event {}".format(process, job_id))
    result = event_client.retrieve_job(process, job_id)
    if (result['status'] == 'incomplete') or (result['status'] == 'running') or (result['status'] == 'submitted'):
        get_logger().info("Job incomplete, retrying")
        raise self.retry()

    get_logger().debug("Handling result for " + json.dumps(event))

    if result['status'] == 'failure':
        get_logger().fatal("Event failed: "+json.dumps(result))
    else:
        get_logger().info("Event succeeded: "+json.dumps(result))
        # TODO
        # 1. update metadata
        # 2. schedule new events as required

    return event['event_id']



###Qrp###
def parse_db_infos(database):
    """Parse database name and extract db_prefix and db_type. Also extract release and assembly for species databases"""
    if species_pattern.match(database):
        m = species_pattern.match(database)
        db_prefix = m.group('prefix')
        db_type = m.group('type')
        release = m.group('release')
        assembly = m.group('assembly')
        return db_prefix, db_type, release, assembly
    elif compara_pattern.match(database):
        m = compara_pattern.match(database)
        division = m.group('division')
        db_prefix = division if division else 'vertebrates'
        return db_prefix, 'compara', None, None
    elif ancestral_pattern.match(database):
        m = ancestral_pattern.match(database)
        division = m.group('division')
        db_prefix = division if division else 'vertebrates'
        return db_prefix, 'ancestral', None, None
    else:
        raise ValueError("Database type for "+database+" is not expected. Please contact the Production team")


def prepare_payload(spec):
    """Prepare payload to run production pipeline"""
    try:
        src_url = make_url(spec['src_uri'])
        (db_prefix, db_type, release, assembly) = parse_db_infos(src_url.database)
        workflow = WorkflowDispatcher(db_type)
        return workflow.create_template(spec, species='anopheles_gambiae')
    except Exception as e:
        return {}


def initiate_pipeline(spec, event={}, rerun=False):
     """Initiates the qrp pipelines for given payload """

     try:

         # prepare the payload with production pipelines based on dbtype and division
         spec.update(prepare_payload(spec))
         # spec = prepare_payload(spec)

         if 'flow' not in spec:
             raise('Flow is not defined')

         spec['job_status'] = 'inprogress'

         if rerun:
             qrp_clinet.update_record(spec)
         else:
             qrp_clinet.insert_record(spec)

         monitor_process_pipeline.delay(spec)
         return {'status': True, 'error': ''}
     except Exception as e:
         spec['status'] = False
         spec['error'] = str(e)
         qrp_clinet.update_record(spec)
         return {'status': False, 'error': str(e)} 

@app.task(bind=True)
def monitor_process_pipeline(self, spec):
     """Process the each pipeline object declared in flow"""
     try:

         if  spec.get('status', False):
             if len(spec.get('flow',[])) > 0:
                 job = spec['flow'].pop(0)
                 spec['current_job'] = job
                 spec['job_status'] = 'inprogress'
                 #pipeline_status.insert_record(spec)
                 qrp_clinet.update_record(spec)
                 qrp_run_pipeline.delay(job, spec)

             elif  len(spec.get('flow', [])) == 0:
                 spec['job_status'] = 'done'
                 spec['current_job'] = {}  
                 qrp_clinet.update_record(spec)
         else :
             spec['job_status'] = 'error'
             qrp_clinet.insert_record(spec)

     except Exception as e :
         spec['job_status'] = 'error'
         spec['error'] = str(e)
         qrp_clinet.update_record(spec)
     return True

@app.task(bind=True)
def qrp_run_pipeline(self, run_job, global_spec):
     """Celery worker  to initiate pipeline and its beekeeper"""

     try :
         temp = construct_pipeline(run_job, global_spec)
         #execute remote command over ssh 
         exece = RemoteCmd(mysql_url=temp['mysql_url'])
         global_spec['hive_db_uri'] = temp['mysql_url']
         qrp_clinet.update_record(global_spec)

         job = exece.run_job(command=' '.join(temp['init']['command']), args=temp['init']['args'],
                             stdout=temp['init']['stdout'], stderr=temp['init']['stderr'])
         print(job)

         if job['status']:
             #run beekeeper 
             job = exece.run_job(command=' '.join(temp['beekeeper']['command']),
                                  args=temp['beekeeper']['args'], stdout=temp['beekeeper']['stdout'], stderr=temp['beekeeper']['stderr'])
             beekeeper_status = exece.beekeper_status()
             print('HIIIIIIIII')
             print(job)
             if beekeeper_status['status'] and beekeeper_status['value'] == 'NO_WORK':
                 global_spec['status'] = True
                 global_spec['completed_jobs'].append(global_spec['current_job'])
                 global_spec['current_job'] = {}
             else:
                 global_spec['status'] = False
                 global_spec['error'] = beekeeper_status['value']
         else:
             global_spec['status'] = False
             global_spec['error'] = job['error']

         monitor_process_pipeline.delay(global_spec)
         return run_job['PipelineName'] + ' : done'

     except Exception as e:
         global_spec['status'] = False
         global_spec['error'] =  str(e)
         monitor_process_pipeline.delay(global_spec)  
         return run_job['PipelineName'] + ' : Exception error: ' + str(e)
