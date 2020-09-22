{% extends "base.json.tpl" %}

{% block flow %}
    {% block coreStats %}
        {
            "PipelineName": "CoreStats",
            "PipeConfig": "Bio::EnsEMBL::Production::Pipeline::PipeConfig::CoreStatistics_conf",
            "PipeParams": {
                "params": {
                    "-registry": "/nfs/panda/ensembl/production/registries/st5-w.pm",
                    {{ pipe_param('species', species) }}
                    {{ pipe_param('division', division)  }}
                    "pipeline_name": "rr_core_stats_{{ species }}_{{ spec['ENS_VERSION'] }}",
                    "-skip_metadata_check": 1,
                },
                "arguments":[],
                "environ":{
                    "ENS_VERSION": "{{ spec['ENS_VERSION'] }}"
                }
            }
        },
    {% endblock coreStats %}
    {% block proteinFeature %}
        {
            "PipelineName": "ProteinFeatures",
            "PipeConfig": "Bio::EnsEMBL::Production::Pipeline::PipeConfig::ProteinFeatures_conf",
            "PipeParams": {
                "params": {
                    "-registry": "/nfs/panda/ensembl/production/registries/st5-w.pm",
                    {{ pipe_param('species', species) }}
                    {{ pipe_param('division', division)  }}
                    "-pipeline_dir": "/hps/nobackup2/production/ensembl/ensprod/temp/protein_features",
                    "-antispecies": "homo_sapiens",
                    "-interpro_desc_source": "core_dbs",
                    "-pipeline_name": "rr_protein_features_{{ species }}_{{ spec['ENS_VERSION'] }}",
                    "-interpro_desc_source": "core_dbs",
                    "-interproscan_version": {{ env['INTERPRO_VERSION'] }},
                    "-skip_checksum_loading": 1
                },
                "arguments": [],
                "environ": {}
            }
        }
    {% endblock proteinFeature %}
    {% block FTPDumps %}
        {
            "PipelineName": "FTPDumps",
            "PipeConfig": "Bio::EnsEMBL::Production::Pipeline::PipeConfig::DumpCore_vertebrates_conf",
            "PipeParams": {
                "params": {
                    "-registry": "/nfs/panda/ensembl/production/registries/st5.pm",
                    "-ensembl_cvs_root_dir": {{ env['BASE_DIR'] }},
                    "-pipeline_name": "rr_ftp_dump_{{ species }}_{{ spec['ENS_VERSION'] }}",
                    "-release": {{ env['ENS_VERSION'] }},
                    {{ pipe_param('species', species) }}
                    {{ pipe_param('division', division)  }}
                    "-ftp_dir": "/hps/nobackup2/production/ensembl/ensprod/release_dumps/rapid-release-{{ env['RR_VERSION'] }} ",
                    "-skip_metadata_check": 1,
                    "-abinitio": 0,
                    "-skip_convert_fasta": 1,
                    "-skip_blat": 1
                },
                "arguments": [],
                "environ": {}
            }
        }
    {% endblock FTPDumps %}
{% endblock flow %}
