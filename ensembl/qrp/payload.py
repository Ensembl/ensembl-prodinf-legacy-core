payload={

  "core":{
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

  "variation":{
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
    ]
  }
}
