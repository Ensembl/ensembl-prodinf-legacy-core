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
               "-registry": "/homes/ensprod/vinay_test/vinay.reg",
               "-species" : "{{species if species else '' }}" ,
               "-division": "{{ division if division else 'vertebrates,metazoa,fungi,protists,plants' }}",
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
