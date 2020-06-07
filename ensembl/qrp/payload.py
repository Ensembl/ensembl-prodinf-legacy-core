payload={

  "test":{
    "flow":[
      {
        "PipelineName": "CoreStats",   
        "PipeConfig": "Bio::EnsEMBL::Production::Pipeline::PipeConfig::CoreStatistics_conf",
        "PipeParams": {
          "params":{
            "-registry": "/homes/ensprod/vinay_test/vinay.reg",
            "-species" : "anopheles_gambiae",
            "-skip_metadata_check": 1,        
          },
          "arguments":[],
          "environ": {
            "ENS": 101
          }
        }         
      },
      {
       "PipelineName": "Add_num",   
       "PipeConfig": "Bio::EnsEMBL::Hive::Examples::LongMult::PipeConfig::LongMult_conf",
       "PipeParams": {
         "params":{
         },
         "arguments":[],
         "environ": {
           "ENS": 101
         }
       }         
     }
    ],
   "hive_url": "mysql://ensadmin:ensembl@mysql-ens-hive-prod-1:4575/" ,
   "ENS_VERSION": 100,
   "EG_VERSION": 47,
   "contact":"vinay@ebi.ac.uk",
   "comment":"testing handover for qrp", 
   "status": "false",
   "user": "vinay" 
  },

  "core":{
    "flow":[
      {
        "PipelineName": "CoreStats",   
        "PipeConfig": "Bio::EnsEMBL::Production::Pipeline::PipeConfig::CoreStatistics_conf",
        "PipeParams": {
          "params":{
            "-registry": "${BASE_DIR}/ensembl-production_private/release_coordination/registries/reg_ens-sta-5_rw.pm",
            "-species": "{species}",
            "-division": "{division}",
            "-antispecies": "{antispecies}"
          },
          "arguments":[],
          "environ": {
          }
         }
        },
        {
          "PipelineName": "ProteinFeatures",
          "PipeConfig": "Bio::EnsEMBL::Production::Pipeline::PipeConfig::ProteinFeatures_conf",
          "PipeParams": {
            "params":{
              "-registry": "${REG_FILE_VERT}",
              "-pipeline_dir": "${PIPELINE_DIR}",
              "-interpro_desc_source": "core_dbs",
              "-species": "{species}",
              "-division": "{division}", 
              "-antispecies": "{antispecies}"
            },
            "arguments":[],
            "environ": {
              "PIPELINE_DIR": "/hps/nobackup2/production/ensembl/ensprod/temp/protein_features",
              "REG_DIR": "${BASE_DIR}/ensembl-production_private/release_coordination/registries",
              "REG_FILE_VERT": "${REG_DIR}/reg_ens-sta-5_rw.pm",
           }

         }
       },
      {
        "PipelineName": "FTPDUMPS_NONVERT",
        "PipeConfig": "Bio::EnsEMBL::Production::Pipeline::PipeConfig::DumpCore_non_vertebrates_conf",
        "PipeParams": {
          "params":{
            "-registry": "${BASE_DIR}/ensembl-production_private/release_coordination/registries/reg_ens-sta-5_rw.pm",
            "-ensembl_cvs_root_dir": "$BASE_DIR",
            "-release": "$EG_VERSION",
            "-ftp_dir": "/hps/nobackup2/production/ensembl/ensprod/release_dumps/rapid-release/",
            "-species": "{species}",
            "-division": "{division}",
            "-antispecies": "{antispecies}"
          },
          "arguments":[],
          "environ": {
          }
         }
      },
      {
        "PipelineName": "FTPDUMPS_VERT",
        "PipeConfig": "Bio::EnsEMBL::Production::Pipeline::PipeConfig::DumpCore_vertebrates_conf",
        "PipeParams": {
          "params":{
            "-registry": "${BASE_DIR}/ensembl-production_private/release_coordination/registries/reg_ens-sta-5_rw.pm",
            "-ensembl_cvs_root_dir": "$BASE_DIR",
            "-release": "$EG_VERSION",
            "-ftp_dir": "/hps/nobackup2/production/ensembl/ensprod/release_dumps/rapid-release/",
            "-species": "{species}",
            "-division": "{division}",
            "-antispecies": "{antispecies}"
          },
          "arguments":[],
          "environ": {
          }
         }
       },
      {
        "PipelineName": "MSQLDUMPS",
        "PipeConfig": "Bio::EnsEMBL::Production::Pipeline::PipeConfig::MySQLDumping_conf",
        "PipeParams": {
          "params":{
            "-meta_database":  "$METADATA_DB",
            "-release": "$ENS_VERSION",
            "-ensembl_cvs_root_dir": "$BASE_DIR",
            "-with_release": 0,   
            "-species": "{species}",
            "-division": "{division}",
            "-antispecies": "{antispecies}"
          },
          "arguments":["$($SRV details script)", "$($METADATA_SRV details prefix_meta_)"],
          "environ": {
            "SRV": "mysql-ens-sta-5-ensprod",
            "METADATA_SRV": "mysql-ens-meta-prod-1",
            "METADATA_DB": "ensembl_metadata_qrp"   
          }
         }
       }       
    ]    
  },

  "variation": {
    "flow":[
      {
       "PipelineName": "Add_num",
       "PipeConfig": "Bio::EnsEMBL::Hive::Examples::LongMult::PipeConfig::LongMult_conf",
       "PipeParams": {
         "params":{
         },
         "arguments":[],
         "environ": {
           "ENS": 101
         }
       }
     },
     [
     {
       "PipelineName": "Add_num_2",
       "PipeConfig": "Bio::EnsEMBL::Hive::Examples::LongMult::PipeConfig::LongMult_conf",
       "PipeParams": {
         "params":{
         },
         "arguments":[],
         "environ": {
           "ENS": 101
         }
       }
     },

     {
       "PipelineName": "Add_num_3",
       "PipeConfig": "Bio::EnsEMBL::Hive::Examples::LongMult::PipeConfig::LongMult_conf",
       "PipeParams": {
         "params":{
         },
         "arguments":[],
         "environ": {
           "ENS": 101
         }
       }
     }
    ] 
   ],
   "hive_url": "mysql://ensadmin:ensembl@mysql-ens-hive-prod-1:4575/" ,
   "ENS_VERSION": 100,
   "EG_VERSION": 47,
   "contact":"vinay@ebi.ac.uk",
   "comment":"testing handover for qrp",
   "status": "false",
   "user": "vinay"
  }

}
