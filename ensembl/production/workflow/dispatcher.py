import os
import json
import jinja2
import re


class WorkflowDispatcher():

    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tpl')
    templateLoader = jinja2.FileSystemLoader(template_dir)
    templateEnv = jinja2.Environment(loader=templateLoader)

    def __init__(self, dbtype, division=None, species=None ):
        self.template_file = 'core/core.tpl'
        pass

    def create_template(self):
        template = WorkflowDispatcher.templateEnv.get_template(self.template_file)
        flow_json = template.render()
        return json.loads(flow_json)  # this is where to put args to the template renderer


obj = WorkflowDispatcher('core')
flow = obj.create_template()
print(flow)
