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
             "environ":{
                "ENS_VERSION": "100"
              }
           }
        },
      {% endblock coreStat %}
        {
          "PipelineName": "ProteinFeatures",
           "PipeConfig": "Bio::EnsEMBL::Production::Pipeline::PipeConfig::ProteinFeatures_conf",
           "PipeParams": {
             "params": {
               "-registry": "/homes/ensprod/vinay_test/vinay.reg",
               "-species" : "{{species if species else '' }}" ,
               "-division": "{{ division if division else 'vertebrates,metazoa,fungi,protists,plants' }}",
               "-pipeline_dir": "/hps/nobackup2/production/ensembl/ensprod/temp/protein_features",
               "-interpro_desc_source": "core_dbs",
               "-antispecies": "homo_sapiens"
             },
             "arguments":[],
             "environ":{
              "PIPELINE_DIR": "/hps/nobackup2/production/ensembl/ensprod/temp/protein_features",
              "REG_DIR": "${BASE_DIR}/ensembl-production_private/release_coordination/registries",
              "REG_FILE_VERT": "${REG_DIR}/reg_ens-sta-5_rw.pm"
              }
           }
        }
      {% block proteinFeature %}


      {% endblock proteinFeature %}


      ]
    {% endblock flow %}

  {% endblock core %}

{% endblock pipeline %}
