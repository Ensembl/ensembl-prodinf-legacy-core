import os
import json
import jinja2
import re


class WorkflowDispatcher():

    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tpl')
    templateLoader = jinja2.FileSystemLoader(template_dir)
    templateEnv = jinja2.Environment(loader=templateLoader)

    def __init__(self, dbtype, division=None, species=None):
        self.dbtype = dbtype
        self.division = division
        self.species = species

    def _get_template(self):
        if self.species:
            template_file = '{tpl_dir}/{tpl_file}.tpl'.format(tpl_dir=self.dbtype, tpl_file=self.species)
        elif self.division:
            template_file = '{tpl_dir}/{tpl_file}.tpl'.format(tpl_dir=self.dbtype, tpl_file=self.division)
        else:
            template_file = '{tpl_dir}/{tpl_file}.tpl'.format(tpl_dir=self.dbtype, tpl_file=self.dbtype)

        return template_file

    def create_template(self, spec, division=None, species=None, antispecies=None):
        template = WorkflowDispatcher.templateEnv.get_template(self._get_template())
        flow_json = template.render(spec=spec, division=division, species=species, antispecies=antispecies)
        return json.loads(flow_json)  # this is where to put args to the template renderer



#obj = WorkflowDispatcher('core')
#flow = obj.create_template({'handover_token': ''}, division='plants')
#print(flow)
