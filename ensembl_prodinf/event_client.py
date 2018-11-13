#!/usr/bin/env python
import argparse
import logging
import requests
import json
from rest_client import RestClient

class EventClient(RestClient):
    
    """
    Simple client for submitting an event to the event service and checking on progress
    This uses the base RestClient, but all endpoint URIs for checking on submited events
    have process as a path element, so this client combines the job_id and process together
    """
    
    def submit_job(self, event):        
        """Submit an event for processing"""
        logging.info("Submitting job")
        return RestClient.submit_job(self,event)
    
    def list_jobs(self, process):
        """List all jobs for a given process"""
        logging.info("Listing")
        r = requests.get(self.jobs.format(self.uri)+'/'+process)
        r.raise_for_status()    
        return r.json()
    
    def delete_job(self, process, job_id, kill=False):
        return super(EventClient, self).delete_job(process+'/'+str(job_id), kill)

    def retrieve_job_failure(self, process, job_id):
        return super(EventClient, self).retrieve_job_failure(process+'/'+str(job_id))

    def retrieve_job_email(self, process, job_id):
        return super(EventClient, self).retrieve_job_email(process+'/'+str(job_id))

    def retrieve_job(self, process, job_id):
        return super(EventClient, self).retrieve_job(process+'/'+str(job_id))
    
    def collate_jobs(self, output_file, pattern='.*'):
        raise AttributeError("Job collation not supported")    
    
    def processes(self):
        """Retrieve a list of processes that the service can schedule"""
        r = requests.get(self.uri+'processes')
        r.raise_for_status()    
        return r.json()

    def events(self):
        """Retrieve a list of events that the service can handle"""
        r = requests.get(self.uri+'events')
        r.raise_for_status()    
        return r.json()


if __name__ == '__main__':
            
    parser = argparse.ArgumentParser(description='Run HCs via a REST service')

    parser.add_argument('-u', '--uri', help='HC REST service URI', required=True)
    parser.add_argument('-a', '--action', help='Action to take', choices=['submit', 'retrieve', 'list', 'delete', 'events', 'processes'], required=True)
    parser.add_argument('-i', '--job_id', help='HC job identifier to retrieve')
    parser.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
    parser.add_argument('-e', '--event', help='Event as JSON')
    parser.add_argument('-p', '--process', help='Process name')

    args = parser.parse_args()
    
    if args.verbose == True:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s - %(message)s')
    
    if args.uri.endswith('/') == False:
        args.uri = args.uri + '/'    

    client = EventClient(args.uri)
            
    if args.action == 'submit':
        results = client.submit_job(json.loads(args.event))
        for process in results['processes']:
            logging.info('Job submitted for process: '+str(process['process'])+' with ID '+str(process['job_id']))
    
    elif args.action == 'retrieve':
        job = client.retrieve_job(args.process, args.job_id)
        client.print_job(job, print_results=True, print_input=True)
    
    elif args.action == 'list':
        for job in client.list_jobs(args.process):
            client.print_job(job)
    
    elif args.action == 'delete':
        client.delete_job(args.process,args.job_id)
        
    elif args.action == 'events':
        logging.info(client.events())

    elif args.action == 'processes':
        logging.info(client.processes())
