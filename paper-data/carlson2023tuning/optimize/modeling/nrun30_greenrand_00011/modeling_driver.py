import parsl
import sys
import os
import argparse
from parsl.app.app import python_app, bash_app
from parsl.data_provider.files import File

from parsl.config import Config
from parsl.providers import SlurmProvider
from parsl.executors import ThreadPoolExecutor
from parsl.executors import HighThroughputExecutor

parser = argparse.ArgumentParser()
parser.add_argument("-nrun", type=int, default=16, help='')
parser.add_argument("-rundir", type=str, default="", help='')
args = parser.parse_args()

NRUN = args.nrun
EXP_PATH = args.rundir

config = Config(
    executors=[
        ThreadPoolExecutor(
            max_threads=4, 
            label='local_threads'
        ),
        HighThroughputExecutor( 
            label='prlm_htex',
            #address='10.249.0.22',
            max_workers=1,
            #cores_per_worker=4,
            #cpu_affinity='block',
            provider=SlurmProvider(
                account='m1041_g',
                nodes_per_block=1,
                init_blocks=1,
                min_blocks=1,
                max_blocks=1,
                scheduler_options='#SBATCH --constraint=gpu\n#SBATCH --ntasks-per-node=1\n#SBATCH --gpus-per-node=1 --qos=regular',
                worker_init='source /global/homes/m/mcarlson/LandIce/ALITune/optimize/prepare_env.sh',
                #launcher=SrunMPILauncher(),
                walltime='04:00:00',
                cmd_timeout=60,
            ),
        )
    ]
)

config.retries = 2

parsl.load(config)

NUM_RETRIES = 2
TIMEOUT = 500
PYTHON_EXEC = "python"

DB_PATH = EXP_PATH + "/gptune.db/Albany_LandIce_PRLM.json"
DATA_PATH = EXP_PATH + "/../../data"
TUNING_RUNLINE = PYTHON_EXEC + " " + EXP_PATH + "/albany_tune_RCI.py -nrun {}".format(NRUN)
ALBANY_RUNLINE = PYTHON_EXEC + " " + EXP_PATH + "/albany_driver.py"

@python_app(executors=["local_threads"])
def get_num_function_evals(tuning_runline, inputs=[], outputs=[]):
    import subprocess
    subprocess.call(tuning_runline, shell=True)

    import json
    file = open(inputs[0].filepath, "r")
    data = json.load(file)
    file.close()

    func_evals = data['func_eval']
    mask = [fe['evaluation_result']['runtime'] == None for fe in func_evals]
    func_evals = [i for (i, v) in zip(func_evals, mask) if v]

    return len(func_evals)

@python_app(executors=["local_threads"])
def get_function_eval_configs(num_func_evals, inputs=[], outputs=[]):

    import json
    file = open(inputs[0].filepath, "r")
    data = json.load(file)
    file.close()
    
    func_evals = data['func_eval']
    mask = [fe['evaluation_result']['runtime'] == None for fe in func_evals]
    func_evals = [i for (i, v) in zip(func_evals, mask) if v]

    for k in range(num_func_evals):
        file = open(outputs[k].filepath, "w")
        json.dump(func_evals[k], file)
        file.close()

    return 0

@bash_app(executors=["prlm_htex"])
def evaluate_function(albany_runline, data_dir, inputs=[], outputs=[], nprocs=1, stderr=parsl.AUTO_LOGNAME, stdout=parsl.AUTO_LOGNAME):

    import json
    file = open(inputs[0].filepath, "r")
    data = json.load(file)
    file.close()

    mesh = data['task_parameter']['mesh']
    ms1_smoother_name = data['tuning_parameter']['ms1_smoother_name']
    ms1_relaxation_num_sweeps = data['tuning_parameter']['ms1_num_sweeps']
    ms1_relaxation_damping_factor = data['tuning_parameter']['ms1_damping_factor']
    ms1_relaxation_inner_damping_factor = data['tuning_parameter']['ms1_inner_damping_factor']
    ms1_chebyshev_degree = data['tuning_parameter']['ms1_chebyshev_degree']
    ms1_chebyshev_eig_ratio = data['tuning_parameter']['ms1_eigenvalue_ratio']
    ms1_chebyshev_max_iters = data['tuning_parameter']['ms1_chebyshev_maxiters']
    ms4_smoother_name = data['tuning_parameter']['ms4_smoother_name']
    ms4_relaxation_num_sweeps = data['tuning_parameter']['ms4_num_sweeps']
    ms4_relaxation_damping_factor = data['tuning_parameter']['ms4_damping_factor']
    ms4_relaxation_inner_damping_factor = data['tuning_parameter']['ms4_inner_damping_factor']
    ms4_chebyshev_degree = data['tuning_parameter']['ms4_chebyshev_degree']
    ms4_chebyshev_eig_ratio = data['tuning_parameter']['ms4_eigenvalue_ratio']
    ms4_chebyshev_max_iters = data['tuning_parameter']['ms4_chebyshev_maxiters']

    runline  = "srun -n 1 "
    runline += albany_runline + " "
    runline += "-mesh {} ".format(mesh)
    runline += "-ms1_smoother_name {} ".format(ms1_smoother_name)
    runline += "-ms1_relaxation_num_sweeps {} ".format(ms1_relaxation_num_sweeps)
    runline += "-ms1_relaxation_damping_factor {} ".format(ms1_relaxation_damping_factor)
    runline += "-ms1_relaxation_inner_damping_factor {} ".format(ms1_relaxation_inner_damping_factor)
    runline += "-ms1_chebyshev_degree {} ".format(ms1_chebyshev_degree)
    runline += "-ms1_chebyshev_eig_ratio {} ".format(ms1_chebyshev_eig_ratio)
    runline += "-ms1_chebyshev_max_iters {} ".format(ms1_chebyshev_max_iters)
    runline += "-ms4_smoother_name {} ".format(ms4_smoother_name)
    runline += "-ms4_relaxation_num_sweeps {} ".format(ms4_relaxation_num_sweeps)
    runline += "-ms4_relaxation_damping_factor {} ".format(ms4_relaxation_damping_factor)
    runline += "-ms4_relaxation_inner_damping_factor {} ".format(ms4_relaxation_inner_damping_factor)
    runline += "-ms4_chebyshev_degree {} ".format(ms4_chebyshev_degree)
    runline += "-ms4_chebyshev_eig_ratio {} ".format(ms4_chebyshev_eig_ratio)
    runline += "-ms4_chebyshev_max_iters {} ".format(ms4_chebyshev_max_iters)
    runline += "-input {} ".format(data_dir)
    runline += "-output {} ".format(outputs[0].filepath)
    runline += "-timelimit 500 "

    return runline + "|| echo \"\""

@python_app(executors=["local_threads"])
def get_evaluation_result(inputs=[], outputs=[]):
    import json
    file = open(inputs[0].filepath, "r")
    data = json.load(file)
    file.close()

    try:
        file = open(inputs[1].filepath, "r")
        lines = file.readlines()
        solve_time = float(lines[0])
        file.close()
        data['evaluation_result']['runtime'] = solve_time
    except:
        data['evaluation_result']['runtime'] = 1e12

    file = open(outputs[0].filepath, "w")
    json.dump(data, file)
    file.close()

    os.system("rm -rf {}".format(inputs[0].filepath))
    os.system("rm -rf {}".format(inputs[1].filepath))

    return 0

@python_app(executors=["local_threads"])
def update_database(inputs=[], outputs=[]):

    import json
    file = open(outputs[0].filepath, "r")
    db_data = json.load(file)
    file.close()

    func_evals = db_data['func_eval']

    for input in inputs:
        file = open(input.filepath, "r")
        eval_data = json.load(file)
        file.close()

        # get uid from eval_data
        uid = eval_data['uid']

        # find db_data entry with matching uid
        idx = [index for index,value in enumerate(func_evals) if value['uid'] == uid]

        # update db_data
        func_evals[idx[0]] = eval_data

        os.system("rm -rf {}".format(input.filepath))

    os.system("rm -rf {}".format(outputs[0].filepath))
    file = open(outputs[0].filepath, "w")
    json.dump(db_data, file)
    file.close()

    return 0

# 1) get number of function evaluations
requested_num_evals = get_num_function_evals(TUNING_RUNLINE, inputs=[File(DB_PATH)], outputs=[File(DB_PATH)])
num_func_evals = requested_num_evals.result()

while num_func_evals > 0:

    # 2) create function evaluation configuration files
    requested_eval_configs = get_function_eval_configs(num_func_evals, 
                                                       inputs=[requested_num_evals.outputs[0]], 
                                                       outputs=[File(EXP_PATH+"/data/eval_configs.{}.json".format(k)) for k in range(num_func_evals)])

    # 3) do function evaluations
    function_evaluated = []
    for k in range(num_func_evals):
        function_evaluated.append(evaluate_function(ALBANY_RUNLINE, DATA_PATH,
                                                    inputs=[requested_eval_configs.outputs[k]],
                                                    outputs=[File(EXP_PATH+"/data/solvetime.{}.txt".format(k))]))

    # 4) get function evaluations
    evaluation_results = []
    for k in range(num_func_evals):
        evaluation_results.append(get_evaluation_result(inputs=[requested_eval_configs.outputs[k], function_evaluated[k].outputs[0]],
                                                        outputs=[File(EXP_PATH+"/data/fn_eval.{}.json".format(k))]))

    # 5) write function evaluations to database
    database_updated = update_database(inputs=[i.outputs[0] for i in evaluation_results], 
                                       outputs=[File(DB_PATH)])

    # 6) get remaining number of function evaluations
    requested_num_evals = get_num_function_evals(TUNING_RUNLINE, inputs=[database_updated.outputs[0]], outputs=[File(DB_PATH)])
    num_func_evals = requested_num_evals.result()

