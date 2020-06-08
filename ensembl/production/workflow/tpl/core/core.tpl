{% extends "base.tpl" %}

{% block pipeline %}

  {% block core %}
      {% block flow %}
      "flow" : [
       {% block coreStat %}
        {
          "PipelineName": "CoreStats",
           "PipeConfig": "Bio::EnsEMBL::Production::Pipeline::PipeConfig::CoreStatistics_conf",
           "PipeParams": {
             "params": {
               "-registry": "registry.reg",
               "-species" : "{{species if species else 'vertebrates, metazoa, fungi, protists, plants' }}" ,
               "-division": "{{ division if division else '' }}",
               "-skip_metadata_check": 1,
               "-run_all": 1
             },
             "arguments":[],
             "environ":{ }
           }
        }
      {% endblock coreStat %}

      ]
    {% endblock flow %}

  {% endblock core %}

{% endblock pipeline %}
