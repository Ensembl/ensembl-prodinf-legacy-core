'''
Tasks and entrypoint need to accept and sequentially process a database. 
The data flow is:
1. handover_database (standard function)
- checks existence of database
- submits HCs if appropriate and submits celery task process_checked_db
- if not, submits copy and submits celery task process_copied_db
2. process_checked_db (celery task)
- wait/retry until healthcheck job has completed
- if success, submit copy job and submits celery task process_copied_db
3. process_copied_db (celery task)
- wait/retry until copy job has completed
- if success, submit metadata update job and submit celery task process_db_metadata
4. process_db_metadata (celery task)
- wait/retry until metadara load job has completed
- if success, process event using a event handler endpoint celery task
@author: dstaines
'''
from ensembl_prodinf.handover_celery_app import app

from hc_client import HcClient
from db_copy_client import DbCopyClient
from metadata_client import MetadataClient
from event_client import EventClient
from sqlalchemy_utils.functions import database_exists, drop_database
from sqlalchemy.engine.url import make_url
from .utils import send_email
from .models.compara import check_grch37
from .models.core import get_coredb_assembly, get_coredb_genebuild
from .models.metadata import get_metadb_assembly, get_previous_assembly_db_list, get_metadb_genome
import handover_config as cfg
import uuid
import re
import reporting

pool = reporting.get_pool(cfg.report_server)
hc_client = HcClient(cfg.hc_uri)
db_copy_client = DbCopyClient(cfg.copy_uri)
metadata_client = MetadataClient(cfg.meta_uri)
event_client = EventClient(cfg.event_uri)

db_types_list = [i for i in cfg.allowed_database_types.split(",")]
species_pattern = re.compile("(.*[a-z])_(core|rnaseq|cdna|otherfeatures|variation|funcgen)_?[0-9]*?_([0-9]*)_([0-9]*)")
compara_pattern = re.compile(".*[a-z]_(compara)_?([a-z]*)?_?([a-z]*)?_?[0-9]*?_[0-9].*")
ancestral_pattern = re.compile("(.*[a-z])_(ancestral)_[0-9]*")

def get_logger():    
    return reporting.get_logger(pool, cfg.report_exchange, 'handover', None, {})
                
def handover_database(spec):    
    """ Method to accept a new database for incorporation into the system 
    Argument is a dict with the following keys:
    * src_uri - URI to database to handover (required) 
    * tgt_uri - URI to copy database to (optional - generated from staging and src_uri if not set)
    * contact - email address of submitter (required)
    * type - string describing type of update (required)
    * comment - additional information about submission (required)
    The following keys are added during the handover process:
    * handover_token - unique identifier for this particular handover invocation
    * hc_job_id - job ID for healthcheck process
    * db_job_id - job ID for database copy process
    * metadata_job_id - job ID for the metadata loading process
    * progress_total - Total number of task to do
    * progress_complete - Total number of task completed
    """
    # TODO verify dict    
    reporting.set_logger_context(get_logger(), spec['src_uri'], spec)    
    # create unique identifier
    spec['handover_token'] = str(uuid.uuid1())
    spec['progress_total']=3
    check_db(spec['src_uri'])
    src_url = make_url(spec['src_uri'])
    #Scan database name and retrieve species or compara name, database type, release number and assembly version
    (db_prefix, db_type, release, assembly) = parse_db_infos(src_url.database)
    # Check if the given database can be handed over
    if db_type not in db_types_list:
        get_logger().error("Handover failed, " + spec['src_uri'] + " has been handed over after deadline. Please contact the Production team")
        raise ValueError(spec['src_uri'] + " has been handed over after the deadline. Please contact the Production team")
    if 'collection' not in db_prefix and db_type == 'core':
        #Check if this is a new genebuild
        spec = check_new_genebuild(spec,cfg.metadata_uri,db_prefix,release,db_type)
        #Check if this is a new assembly
        spec = check_new_assembly(spec,cfg.metadata_uri,db_prefix,release,db_type)
    #Get database hc group and compara_uri
    (groups,compara_uri) = hc_groups(db_type,db_prefix,spec['src_uri'])
    #Check to which staging server the database need to be copied to
    (spec,staging_uri) = check_staging_server(spec,db_type,db_prefix,assembly)
    #setting compara url to default value for species databases. This value is only used by Compara healthchecks
    if compara_uri is None:
        compara_uri=cfg.compara_uri + 'ensembl_compara_master'
    if 'tgt_uri' not in spec:
        spec['tgt_uri'] = get_tgt_uri(src_url,staging_uri)
    spec['staging_uri'] = staging_uri
    spec['progress_complete']=1
    get_logger().info("Handling " + str(spec))
    submit_hc(spec, groups, compara_uri, staging_uri)
    return spec['handover_token']

def get_tgt_uri(src_url,staging_uri):
    """Create target URI from staging details and name of source database"""
    return str(staging_uri) + str(src_url.database)

    
def check_db(uri):    
    """Check if source database exists"""
    if not database_exists(uri):
        get_logger().error("Handover failed, " + uri + " does not exist")
        raise ValueError(uri + " does not exist")
    else:
        return

def parse_db_infos(database):
    """Parse database name and extract db_prefix and db_type. Also extract release and assembly for species databases"""
    if species_pattern.match(database):
        db_prefix = species_pattern.match(database).group(1)
        db_type = species_pattern.match(database).group(2)
        release = species_pattern.match(database).group(3)
        assembly = species_pattern.match(database).group(4)
        return db_prefix, db_type, release, assembly
    elif compara_pattern.match(database):
        db_type = compara_pattern.match(database).group(1)
        db_prefix = compara_pattern.match(database).group(2)
        return db_prefix, db_type, None, None
    elif ancestral_pattern.match(database):
        db_prefix = ancestral_pattern.match(database).group(1)
        db_type = ancestral_pattern.match(database).group(2)
        return db_prefix, db_type, None, None
    else:
        raise ValueError("Database type for "+database+" is not expected. Please contact the Production team")

def hc_groups(db_type,db_prefix,uri):
    """Find which HC group to run on a given database type. For Compara generate the compara master uri"""
    if db_type in ['core','rnaseq','cdna','otherfeatures']:
        return [cfg.core_handover_group],None
    elif db_type == 'variation':
        return [cfg.variation_handover_group],None
    elif db_type == 'funcgen':
        return [cfg.funcgen_handover_group],None
    elif db_type == 'ancestral':
        return [cfg.ancestral_handover_group],None
    elif db_type == 'compara':
        if  db_prefix == "pan":
            compara_uri=cfg.compara_uri + db_prefix + '_compara_master'
            compara_handover_group=cfg.compara_pan_handover_group
        elif check_grch37(uri,'homo_sapiens'):
            compara_uri=cfg.compara_uri + 'ensembl_compara_master_grch37'
            compara_handover_group=cfg.compara_handover_group
        elif db_prefix:
            compara_uri=cfg.compara_uri + db_prefix + '_compara_master'
            compara_handover_group=cfg.compara_handover_group
        else:
            compara_uri=cfg.compara_uri + 'ensembl_compara_master'
            compara_handover_group=cfg.compara_handover_group
        return [compara_handover_group],compara_uri
    else:
        raise ValueError("Can't find hc group for "+uri+" Please check handover config file")

def check_staging_server(spec,db_type,db_prefix,assembly):
    """Find which staging server should be use. secondary_staging for GRCh37 and Bacteria, staging for the rest"""
    if 'bacteria' in db_prefix:
        staging_uri = cfg.secondary_staging_uri
    elif db_prefix == 'homo_sapiens' and assembly == '37':
        staging_uri = cfg.secondary_staging_uri
        spec['GRCh37']=1
        spec['progress_total']=2
    elif db_type == 'compara' and check_grch37(spec['src_uri'],'homo_sapiens'):
        staging_uri = cfg.secondary_staging_uri
        spec['GRCh37']=1
        spec['progress_total']=2
    else:
        staging_uri = cfg.staging_uri
    return spec,staging_uri

def check_new_assembly(spec,metadata_uri,species,release,db_type):
    """Check the core database assembly value and compare it with what we have in the Metadata database
    if the assembly doesn't exist in the metadata database then it's a new species, update the handover type
    if the assembly is the same, all good, nothing to do here
    if the assembly is different, make sure that we update the handover type and generate a list of old assembly databases to clean up
    """
    metadata_assembly = get_metadb_assembly(metadata_uri,species,release)
    if metadata_assembly:
        if get_coredb_assembly(spec['src_uri']).meta_value != metadata_assembly.assembly_default:
            get_logger().info(str(species) + ' has a new assembly')
            spec['type']='new_assembly'
            old_assembly_databases_list = get_previous_assembly_db_list(metadata_uri,species,release)
            if old_assembly_databases_list:
                spec['old_assembly_dbs'] = old_assembly_databases_list
    else:
        spec['type']='new_assembly'
        get_logger().info(str(species) + ' has a new assembly')
    return spec

def check_new_genebuild(spec,metadata_uri,species,release,db_type):
    """Check the core database genebuild.version or (genebuild.start_date/genebuild.last_geneset_update) value and compare it with what we have in the Metadata database
    if the Genebuild is the same, all good, nothing to do here
    if the Genebuild is different, make sure that we update the handover type
    """
    metadata_genome = get_metadb_genome(metadata_uri,species,release)
    if metadata_genome:
        if get_coredb_genebuild(spec['src_uri']) != metadata_genome.genebuild:
            get_logger().info(str(species) + ' has a new genebuild')
            spec['type']='new_genebuild'
    return spec

def submit_hc(spec, groups, compara_uri, staging_uri):
    """Submit the source database for healthchecking. Returns a celery job identifier"""
    hc_job_id = hc_client.submit_job(spec['src_uri'], cfg.production_uri, compara_uri, staging_uri, cfg.live_uri, None, groups, cfg.data_files_path, None, spec['handover_token'])
    spec['hc_job_id'] = hc_job_id
    task_id = process_checked_db.delay(hc_job_id, spec)
    get_logger().debug("Submitted DB for checking as " + str(task_id))
    return task_id

@app.task(bind=True)
def process_checked_db(self, hc_job_id, spec):
    """ Task to wait until HCs finish and then respond e.g.
    * submit copy if HCs succeed
    * send error email if not
    """
    reporting.set_logger_context(get_logger(), spec['src_uri'], spec)    
    # allow infinite retries 
    self.max_retries = None
    get_logger().info("HCs in progress, please see: " +cfg.hc_web_uri + str(hc_job_id))
    result = hc_client.retrieve_job(hc_job_id)
    if result['status'] in ['incomplete', 'running', 'submitted']:
        get_logger().debug("HC Job incomplete, checking again later")
        raise self.retry()
    
    # check results
    if result['status'] == 'failed':
        get_logger().info("HCs failed to run, please see: "+cfg.hc_web_uri + str(hc_job_id))
        msg = """
Running healthchecks on %s failed to execute.
Please see %s
""" % (spec['src_uri'], cfg.hc_web_uri + str(hc_job_id))
        send_email(to_address=spec['contact'], subject='HC failed to run', body=msg, smtp_server=cfg.smtp_server)
        return 
    elif result['output']['status'] == 'failed':
        get_logger().info("HCs found problems, please see: "+cfg.hc_web_uri + str(hc_job_id))
        msg = """
Running healthchecks on %s completed but found failures.
Please see %s
""" % (spec['src_uri'], cfg.hc_web_uri + str(hc_job_id))
        send_email(to_address=spec['contact'], subject='HC ran but failed', body=msg, smtp_server=cfg.smtp_server)
        return
    else:
        get_logger().info("HCs fine, starting copy")
        spec['progress_complete']=2
        submit_copy(spec)

def drop_old_assembly_databases(spec):
    """Drop databases on a previous assembly from the staging MySQL server"""
    if 'old_assembly_dbs' in spec:
        for database in spec['old_assembly_dbs']:
            db_uri = spec['staging_uri'] + database
            if database_exists(db_uri):
                get_logger().info("Dropping " + str(db_uri))
                drop_database(db_uri)
    else:
        return

def submit_copy(spec):
    """Submit the source database for copying to the target. Returns a celery job identifier"""
    drop_old_assembly_databases(spec)   
    copy_job_id = db_copy_client.submit_job(spec['src_uri'], spec['tgt_uri'], None, None, False, True, None)
    spec['copy_job_id'] = copy_job_id
    task_id = process_copied_db.delay(copy_job_id, spec)    
    get_logger().debug("Submitted DB for copying as " + str(task_id))
    return task_id


@app.task(bind=True)    
def process_copied_db(self, copy_job_id, spec):
    """Wait for copy to complete and then respond accordingly:
    * if success, submit to metadata database
    * if failure, flag error using email"""
    reporting.set_logger_context(get_logger(), spec['src_uri'], spec)    
    # allow infinite retries     
    self.max_retries = None
    get_logger().info("Copying in progress, please see: " +cfg.copy_web_uri + str(copy_job_id))
    result = db_copy_client.retrieve_job(copy_job_id)
    if result['status'] in ['incomplete', 'running', 'submitted']:
        get_logger().debug("Database copy job incomplete, checking again later")
        raise self.retry()
    if result['status'] == 'failed':
        get_logger().info("Copy failed, please see: "+cfg.copy_web_uri + str(copy_job_id))
        msg = """
Copying %s to %s failed.
Please see %s
""" % (spec['src_uri'], spec['tgt_uri'], cfg.copy_web_uri + str(copy_job_id))
        send_email(to_address=spec['contact'], subject='Database copy failed', body=msg, smtp_server=cfg.smtp_server)
        return
    elif 'GRCh37'in spec:
        get_logger().info("Copying complete, Handover successful")
        spec['progress_complete']=2
    else:
        get_logger().info("Copying complete, submitting metadata job")
        spec['progress_complete']=3
        submit_metadata_update(spec)

def submit_metadata_update(spec):
    """Submit the source database for copying to the target. Returns a celery job identifier."""
    metadata_job_id = metadata_client.submit_job( spec['tgt_uri'], None, None, None, None, spec['contact'], spec['type'], spec['comment'], 'Handover', None)
    spec['metadata_job_id'] = metadata_job_id
    task_id = process_db_metadata.delay(metadata_job_id, spec)
    get_logger().debug("Submitted DB for metadata loading " + str(task_id))
    return task_id


@app.task(bind=True)    
def process_db_metadata(self, metadata_job_id, spec):
    """Wait for metadata update to complete and then respond accordingly:
    * if success, submit event to event handler for further processing
    * if failure, flag error using email"""
    reporting.set_logger_context(get_logger(), spec['tgt_uri'], spec)
    # allow infinite retries
    self.max_retries = None
    get_logger().info("Loading into metadata database, please see: "+cfg.meta_uri + "jobs/"+ str(metadata_job_id))
    result = metadata_client.retrieve_job(metadata_job_id)
    if result['status'] in ['incomplete', 'running', 'submitted']:
        get_logger().debug("Metadata load Job incomplete, checking again later")
        raise self.retry()
    if result['status'] == 'failed':
        get_logger().info("Metadata load failed, please see "+cfg.meta_uri+ 'jobs/' + str(metadata_job_id) + '?format=failures')
        msg = """
Metadata load of %s failed.
Please see %s
""" % (spec['tgt_uri'], cfg.meta_uri+ 'jobs/' + str(metadata_job_id) + '?format=failures')
        send_email(to_address=spec['contact'], subject='Metadata load failed, please see: '+cfg.meta_uri+ 'jobs/' + str(metadata_job_id) + '?format=failures', body=msg, smtp_server=cfg.smtp_server)
        return
    else:
        #get_logger().info("Metadata load complete, submitting event")
        get_logger().info("Metadata load complete, Handover successful")
        #submit_event(spec,result)
    return

def submit_event(spec,result):
    """Submit an event"""
    print(result['output']['events'])
    for event in result['output']['events']:
        print(event)
        event_client.submit_job({"type":event['type'],"genome":event['genome']})
        get_logger().debug("Submitted event to event handler endpoint")
