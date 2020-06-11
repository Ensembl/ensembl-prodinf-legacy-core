def construct_pipeline(job, spec):
    "construct cmd for pipeline to run"
    hive_dbname = spec['user'] + '_' + job['PipelineName'] + '_' + str(spec['ENS_VERSION']) + '_QRP'
    temp = {
        'init': {'command': [], 'args': [], 'stdout': '', 'stderr': ''},
        'beekeeper': {'command': ['beekeeper.pl'], 'args': [], 'stdout': '', 'stderr': ''}
    }
    db_uri = spec['hive_url'] + hive_dbname

    # for init pipeline
    for key, value in job['PipeParams']['params'].items():

        if key == '-division' or key == '-species' or key == '-antispecies':
            for each_item in value.split(','):
                if each_item:
                    temp['init']['args'].append(key)
                    temp['init']['args'].append(each_item)
            continue

        temp['init']['args'].append(key)
        temp['init']['args'].append(value)

    for value in job['PipeParams']['arguments']:
        temp['init']['args'].append(value)

    for key, value in job['PipeParams']['environ'].items():
        temp['init']['command'].append(key + '=' + str(value))
        temp['init']['command'].append(' && ')

    temp['init']['args'].append('-pipeline_url ')
    temp['init']['args'].append(db_uri)
    temp['init']['args'].append('-hive_force_init')
    temp['init']['args'].append(1)

    temp['init']['command'].append('init_pipeline.pl')
    temp['init']['command'].append(job['PipeConfig'])
    temp['init']['command'].append(' ')
    temp['init']['stdout'] = hive_dbname + ".stdout"
    temp['init']['stderr'] = hive_dbname + ".stderr"

    # for beekeeper
    temp['beekeeper']['args'].append('-url')
    temp['beekeeper']['args'].append(db_uri)
    # check if init pipelie has registry as option
    if '-registry' in job['PipeParams']['params']:
        temp['beekeeper']['args'].append('-reg_conf')
        temp['beekeeper']['args'].append(job['PipeParams']['params']['-registry'])

    temp['beekeeper']['args'].append('-loop')
    temp['beekeeper']['stdout'] = hive_dbname + ".beekeeper.stdout"
    temp['beekeeper']['stderr'] = hive_dbname + ".beekeeper.stderr"
    temp['mysql_url'] = db_uri
    return temp

