#!/usr/bin/env python
import argparse
import logging
import requests
from server_utils import assert_http_uri, assert_mysql_db_uri, assert_email

class HandoverClient(object):
    
    """
    Client for submitting databases for handover
    """
    
    handovers = '{}handovers'
    
    def __init__(self, uri):
        assert_http_uri(uri)
        self.uri = uri
    
    def submit_job(self, spec):      
        """
        Arguments:
          spec : dict containing keys `src_uri`, `type`, `comment` and `contact`
        """
        assert_mysql_db_uri(spec['src_uri'])
        assert_email(spec['contact'])
        logging.info("Submitting {} for handover".format(spec['src_uri']))
        logging.debug(spec)
        r = requests.post(self.handovers.format(self.uri), json=spec)
        r.raise_for_status()
        return r.json()

if __name__ == '__main__':
            
    parser = argparse.ArgumentParser(description='Handover a database via a REST service')

    parser.add_argument('-u', '--uri', help='HC REST service URI', required=True)
    parser.add_argument('-a', '--action', help='Action to take', choices=['submit', 'retrieve', 'list', 'delete', 'events', 'processes'], required=True)
    parser.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
    parser.add_argument('-s', '--src_uri', help='URI of database to hand over', required=True)
    parser.add_argument('-e', '--email', help='Email address', required=True)
    parser.add_argument('-t', '--type', help='Update type', required=True, choices=['new_genome','new_genebuild','new_assembly','other'])
    parser.add_argument('-c', '--description', help='Description', required=True)

    args = parser.parse_args()
    
    if args.verbose == True:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s - %(message)s')
    
    if args.uri.endswith('/') == False:
        args.uri = args.uri + '/'    

    client = HandoverClient(args.uri)
            
    if args.action == 'submit':
        
        spec = {
            "src_uri" : args.src_uri,
            "contact" : args.email,
            "type" : args.type,
            "comment" : args.description
            }
        logging.debug(spec)
        job = client.submit_job(spec)
        logging.info('Job submitted with transaction ID '+str(job['job_id']))
    
    else:
        logging.error("Action "+args.action+" not supported")
