{% extends "base.tpl" %}

{% block pipeline %}

  {% block core %}
      {% block flow %}
      "flow" : [
       {% block coreStat %}
        {
          "PipelineName": "CoreStats",
           "PipeConfig": "Bio::EnsEMBL::Production::Pipeline::PipeConfig::CoreStatistics_conf",
           "arguments":[],
           "PipeParams": {
             "-registry": "registry.reg",
             "-species" : {{species if species else '""' }} ,
             "-division": {{division if division else '""' }} ,
             "-antispecies": {{coreStat_antispecies if coreStat_antispecies else '""'}}
           }
        }
      {% endblock coreStat %}

      ]
    {% endblock flow %}

  {% endblock core %}

{% endblock pipeline %}
