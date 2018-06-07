from celery import Celery
import email_celery_app_config

app = Celery('ensembl_prodinf',
             include=['ensembl_prodinf.email_tasks'])

# Load the externalised config module from PYTHONPATH
try:
    import email_celery_app_config
    app.config_from_object('email_celery_app_config')
except:
    logging.warning('Celery email requires email_celery_app_config module')

if __name__ == '__main__':
    app.start()
