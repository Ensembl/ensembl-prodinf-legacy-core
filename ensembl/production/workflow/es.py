from elasticsearch import Elasticsearch, TransportError, NotFoundError
import os
from ensembl_prodinf.config import load_config_yaml, parse_debug_var

config_file_path = os.environ.get('HANDOVER_CONFIG_PATH')
file_config = load_config_yaml(config_file_path)

class PipelineStatus():
    """Update the Production Pipeline Status"""

    def __init__(self):
        config_file_path = os.environ.get('HANDOVER_CONFIG_PATH')
        file_config = load_config_yaml(config_file_path)
        ES_HOST = os.environ.get('ES_HOST', file_config.get('es_host', 'localhost'))
        ES_PORT = os.environ.get('ES_PORT', file_config.get('es_port', '9200'))
        RELEASE = os.environ.get('ENS_RELEASE', file_config.get('ens_release', '100'))
        self.es = Elasticsearch([{'host': ES_HOST, 'port': ES_PORT}])

    def insert_record(self, spec):
        """Post the job """
        try :
            res = self.es.index(index='pipelines',doc_type='jobs',id=spec['handover_token'],body=spec)
            res= self.es.get(index='pipelines',doc_type='jobs',id=spec['handover_token'])
            return {'status': True, 'error': ''}
        except Exception as e :
            return {'status': False, 'error': str(e)}