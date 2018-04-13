#!/usr/bin/env python
import argparse
import logging
import requests
import sys
import re

from rest_client import RestClient
from server_utils import assert_mysql_uri, assert_mysql_db_uri

class MetadataClient(RestClient):

    def write_output(r, output_file):
        if(output_file != None):
            with output_file as f:
                f.write(r.text)  
        
    def submit_job(self, metadata_uri, database_uri, e_release, eg_release, release_date, current_release, email, update_type, comment, source):
        assert_mysql_db_uri(metadata_uri)
        assert_mysql_db_uri(database_uri)

        payload = {
            'metadata_uri':metadata_uri,
            'database_uri':database_uri,
            'e_release':e_release,
            'eg_release':eg_release,
            'release_date':release_date,
            'current_release':current_release,
            'email':email,
            'update_type':update_type,
            'comment':comment,
            'source':source
            }
        return super(MetadataClient, self).submit_job(payload)
        
    def print_job(self, job, print_results=False, print_input=False):
        logging.info("Job %s (%s) to (%s) - %s" % (job['id'], job['input']['metadata_uri'], job['input']['database_uri'], job['status']))
        if print_input == True:
            print_inputs(job['input'])
        if job['status'] == 'complete':
            if print_results == True:
                logging.info("Load result: " + str(job['status']))
                logging.info("Load took: " +str(job['output']['runtime']))
        elif job['status'] == 'running':
            if print_results == True:
                logging.info("Load result: " + str(job['status']))
                logging.info(str(job['progress']['complete'])+"/"+str(job['progress']['total'])+" task complete")
                logging.info("Status: "+str(job['progress']['message']))
        elif job['status'] == 'failed':
            failure_msg = retrieve_job_failure(uri, job['id'])
            logging.info("Job failed with error: "+ str(failure_msg['msg']))

    def print_inputs(self,i):
        logging.info("Metadata URI: " + i['metadata_uri'])
        logging.info("database URI: " + i['database_uri'])
        logging.info("Ensembl release number: " + i['e_release'])
        logging.info("Release date: " + i['release_date'])
        logging.info("Is it the current release: " + i['current_release'])
        if 'eg_release' in i:
            logging.info("EG release number: " + i['eg_release'])
            logging.info("Email of submitter: " + i['email'])
            logging.info("Update_type: " + i['update_type'])
            logging.info("Comment: " + i['comment'])
            logging.info("Source: " + i['source'])

if __name__ == '__main__':
            
    parser = argparse.ArgumentParser(description='Metadata load via a REST service')

    parser.add_argument('-u', '--uri', help='Metadata database REST service URI', required=True)
    parser.add_argument('-a', '--action', help='Action to take', choices=['submit', 'retrieve', 'list', 'delete', 'email', 'kill_job'], required=True)
    parser.add_argument('-i', '--job_id', help='Metadata job identifier to retrieve')
    parser.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
    parser.add_argument('-o', '--output_file', help='File to write output as JSON', type=argparse.FileType('w'))
    parser.add_argument('-f', '--input_file', help='File containing list of metadata and database URIs', type=argparse.FileType('r'))
    parser.add_argument('-m', '--metadata_uri', help='URI of metadata database')
    parser.add_argument('-d', '--database_uri', help='URI of database to load')
    parser.add_argument('-s', '--e_release', help='Ensembl release number')
    parser.add_argument('-r', '--release_date', help='Release date')
    parser.add_argument('-c', '--current_release', help='Is this the current release')
    parser.add_argument('-g', '--eg_release', help='EG release number')
    parser.add_argument('-e', '--email', help='Email where to send the report')
    parser.add_argument('-t', '--update_type', help='Update type, e.g: New assembly')
    parser.add_argument('-n', '--comment', help='Comment')
    parser.add_argument('-b', '--source', help='Source of the database, eg: Handover, Release load')



    args = parser.parse_args()
    
    if args.verbose == True:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s - %(message)s')
    
    if args.uri.endswith('/') == False:
        args.uri = args.uri + '/'

    client = MetadataClient(args.uri)
            
    if args.action == 'submit':

        if args.input_file == None:
            logging.info("Submitting " + args.database_uri + "->" + args.metadata_uri)
            job_id = client.submit_job(args.metadata_uri, args.database_uri, args.e_release, args.eg_release, args.release_date, args.current_release, args.email, args.update_type, args.comment, args.source)
            logging.info('Job submitted with ID '+str(job_id))
        else:
            for line in args.input_file:
                uris = line.split()
                logging.info("Submitting " + uris[0] + "->" + uris[1])
                job_id = client.submit_job(uris[0], uris[1], args.e_release, args.eg_release, args.release_date, args.current_release, args.email, args.update_type, args.comment, args.source)
                logging.info('Job submitted with ID '+str(job_id))
    
    elif args.action == 'retrieve':
    
        job = client.retrieve_job(args.job_id)
        client.print_job(job, print_results=True, print_input=True)
    
    elif args.action == 'list':
    
        jobs = client.list_jobs()   
        for job in jobs:
            client.print_job(job)
    
    elif args.action == 'delete':
        client.delete_job(args.job_id)

    elif args.action == 'email':
        client.results_email(args.job_id, args.email)
        
