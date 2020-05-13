import os
from ensembl_prodinf.config import load_config_yaml


config_file_path = os.environ.get('EVENT_CELERY_CONFIG_PATH')
file_config = load_config_yaml(config_file_path)

broker_url = os.environ.get("CELERY_BROKER_URL",
                            file_config.get('celery_broker_url', 'pyamqp://qrp:qrp@localhost:5672/qrp')) #need to configure for repective server. virtualhost and ques are defined in dev server  
result_backend = os.environ.get("CELERY_RESULT_BACKEND",
                                file_config.get('celery_result_backend', 'rpc://qrp:qrp@localhost:5672/qrp'))
smtp_server = os.environ.get("SMTP_SERVER",
                             file_config.get('smtp_server', 'localhost'))
from_email_address = os.environ.get("FROM_EMAIL_ADDRESS",
                                    file_config.get('from_email_address', 'ensembl-production@ebi.ac.uk'))
retry_wait = int(os.environ.get("RETRY_WAIT",
                                file_config.get('retry_wait', 60)))

task_routes = {
  'ensembl_prodinf.event_tasks': {'queue': 'event'},
  'ensembl_prodinf.event_tasks.qrp_*': {'queue': 'qrp'},
  'ensembl_prodinf.event_tasks.monitor_*': {'queue': 'monitor'}
}
