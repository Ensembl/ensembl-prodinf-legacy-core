import sys
import radical.saga as saga
import json
import re
import time

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


__all__ = ['RemoteCmd']

Base = declarative_base()

class Beekeeper(Base):
    __tablename__ = 'beekeeper'

    beekeeper_id = Column(Integer, primary_key=True)
    cause_of_death = Column(String)
    loop_until     = Column(String)   

    def __repr__(self):
        return "<beekeeper(beekeeper_id='%s', cause_of_death='%s')>" % (
            self.beekeeper_id, self.cause_of_death)



class RemoteCmd():

    def __init__(self, **args):
        self.REMOTE_HOST = args.get('remote_host', "noah-login-01")
        self.ADDRESS = args.get('address', '10.7.95.60')  # Address of your server
        self.USER = args.get('user', 'vinay')  # Username
        self.PASSWORD = args.get('pass', '')  # That's amazing I got the same combination on my luggage!
        self.WORKING_DIR = args.get('pwd', '/homes/vinay/qrp')  # Your working directory
        self.mysql_url = args.get('mysql_url', None) # hive database string  
        self.ctx = saga.Context("ssh")
        self.ctx.user_id = self.USER
        self.session = saga.Session()
        self.session.add_context(self.ctx)
        #hive instance
        self.hive_session = sessionmaker() 
        self.engine = create_engine(self.mysql_url, pool_recycle=3600, echo=False)
        self.hive_session.configure(bind=self.engine)
          
    def run_job(self, **args):
        """
        Execute Remote command through ssh
        return: {'status': boolean, 'error': str, 'state': str }  
        """
        try:
            jd = saga.job.Description()
            jd.executable      = args['command']
            jd.arguments       = args['args']
            jd.output          = args.get("stdout", 'stdout.log')
            jd.error           = args.get("stderr", 'stderr.log')
            jd.working_directory = args.get('pwd', self.WORKING_DIR)
            js = saga.job.Service('ssh://' + self.ADDRESS, session=self.session)
            myjob = js.create_job(jd)
            print("\n...starting job...\n")

            # Now we can start our job.
            myjob.run()
            print("Job ID    : %s" % (myjob.id))
            print("Job State : %s" % (myjob.state))

            print("\n...waiting for job...\n")
            # wait for the job to either finish or fail
            myjob.wait()
            print("Job State : %s" % (myjob.state))
            print("Exitcode  : %s" % (myjob.exit_code))
            if myjob.exit_code !=0 :
                return {'status': False, 'state': myjob.state,  'error': 'Failed to ru nthe job check stderr:' + jd.working_directory}

            return {'status': True, 'error': '', 'state': myjob.state }
        except Exception as e:
            return {'status': False, 'error': str(e) } 
      
    def beekeper_status(self):
        """
        Check beekeeper executed all the jobs 
        """
        s = self.hive_session()
        try:
            result = s.query(Beekeeper).order_by(Beekeeper.beekeeper_id.desc()).first()
            if (result == None):
                return {'status': False, 'error': 'No Records', 'value': ''}
            return {'status': True, 'error': '', 'value': result.cause_of_death}
        finally:
            s.close()
