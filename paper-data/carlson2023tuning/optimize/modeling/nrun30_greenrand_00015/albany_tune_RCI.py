#! /usr/bin/env python3
# GPTune Copyright (c) 2019, The Regents of the University of California,
# through Lawrence Berkeley National Laboratory (subject to receipt of any
# required approvals from the U.S.Dept. of Energy) and the University of
# California, Berkeley.  All rights reserved.
#
# If you have questions about your rights to use or distribute this software,
# please contact Berkeley Lab's Intellectual Property Office at IPO@lbl.gov.
#
# NOTICE. This Software was developed under funding from the U.S. Department
# of Energy and the U.S. Government consequently retains certain rights.
# As such, the U.S. Government has been granted for itself and others acting
# on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in
# the Software to reproduce, distribute copies to the public, prepare
# derivative works, and perform publicly and display publicly, and to permit
# other to do so.
#
################################################################################
"""
Example of invocation of this script:
python3.7 albany_tune_RCI.py -nrun 10

where:
    -nrun is the number of calls per task
"""
 
################################################################################

import sys
import os
import numpy as np
import argparse

sys.path.insert(0, os.path.abspath("/global/homes/m/mcarlson/LandIce/GPTune"))

from gptune import * # import all

################################################################################
def objectives(point):                          
    print('objective is not needed when options["RCI_mode"]=True')

def ALITune(nrun=10):
    
    (machine, processor, nodes, cores) = list(GetMachineConfiguration())
    # print ("machine: " + machine + " processor: " + processor + " num_nodes: " + str(nodes) + " num_cores: " + str(cores))

    TUNER_NAME = 'GPTune'
    os.environ['MACHINE_NAME'] = machine
    
    meshes = ["humboldt-3-20km", "green-3-20km"]
    smoothers = ["MT_Gauss_Seidel", "Two_stage_Gauss_Seidel", "Chebyshev"]

    # Task parameters
    mesh                     = Categoricalnorm (meshes,            transform="onehot",    name="mesh")

    # Input parameters
    ms1_smoother_name        = Categoricalnorm (smoothers,         transform="onehot",    name="ms1_smoother_name")
    ms1_num_sweeps           = Integer         (1,   2,            transform="normalize", name="ms1_num_sweeps")
    ms1_damping_factor       = Real            (0.8, 1.2,          transform="normalize", name="ms1_damping_factor")
    ms1_inner_damping_factor = Real            (0.8, 1.2,          transform="normalize", name="ms1_inner_damping_factor")
    ms1_chebyshev_degree     = Integer         (1,   6,            transform="normalize", name="ms1_chebyshev_degree")
    ms1_eigenvalue_ratio     = Real            (10.0, 50.0,        transform="normalize", name="ms1_eigenvalue_ratio")
    ms1_chebyshev_maxiters   = Integer         (5,   100,          transform="normalize", name="ms1_chebyshev_maxiters")
    ms4_smoother_name        = Categoricalnorm (smoothers,         transform="onehot",    name="ms4_smoother_name")
    ms4_num_sweeps           = Integer         (1,   2,            transform="normalize", name="ms4_num_sweeps")
    ms4_damping_factor       = Real            (0.8, 1.2,          transform="normalize", name="ms4_damping_factor")
    ms4_inner_damping_factor = Real            (0.8, 1.2,          transform="normalize", name="ms4_inner_damping_factor")
    ms4_chebyshev_degree     = Integer         (1,   6,            transform="normalize", name="ms4_chebyshev_degree")
    ms4_eigenvalue_ratio     = Real            (10.0, 50.0,        transform="normalize", name="ms4_eigenvalue_ratio")
    ms4_chebyshev_maxiters   = Integer         (5,   100,          transform="normalize", name="ms4_chebyshev_maxiters")

    # Output parameters
    runtime = Real(-float("Inf"), float("Inf"), name="runtime")

    # Defines spaces
    IS = Space([mesh])
    PS = Space([ms1_smoother_name, ms1_num_sweeps, ms1_damping_factor, ms1_inner_damping_factor, ms1_chebyshev_degree, ms1_eigenvalue_ratio, ms1_chebyshev_maxiters, 
                ms4_smoother_name, ms4_num_sweeps, ms4_damping_factor, ms4_inner_damping_factor, ms4_chebyshev_degree, ms4_eigenvalue_ratio, ms4_chebyshev_maxiters])
    OS = Space([runtime])

    # """ Print all input and parameter samples """ 
    # print(IS, PS, OS)

    problem = TuningProblem(IS, PS, OS, objectives, {}, None, constants={})
    computer = Computer(nodes = nodes, cores = cores, hosts = None)  

    # """ Set and validate options """  
    options = Options()
    options['RCI_mode'] = True
    options['model_processes'] = 1
    options['model_restarts'] = 1
    options['distributed_memory_parallelism'] = False
    options['shared_memory_parallelism'] = False
    options['model_class'] = 'Model_LCM' # 'Model_LCM'
    options['verbose'] = False
    options['sample_algo'] = 'MCS'
    options['sample_class'] = 'SampleOpenTURNS'
    options.validate(computer = computer)
    
    # """ Building MLA with the given list of tasks """
    giventask = [["green-3-20km"]]
    data = Data(problem)
    gt = GPTune(problem, computer=computer, data=data, options=options, driverabspath=os.path.abspath(__file__))        
    
    NI = len(giventask)
    NS = nrun
    #(data, model, stats) = gt.MLA(NS=NS, NI=NI, Igiven=giventask, NS1=max(NS//2, 1))
    (data, model, stats) = gt.MLA(NS=NS, NI=NI, Igiven=giventask, NS1=NS)
    # print("stats: ", stats)

    """ Print all input and parameter samples """   
    for tid in range(NI):
        print("tid: %d"%(tid))
        print("    matrix:%s"%(data.I[tid][0]))
        print("    Ps ", data.P[tid])
        print("    Os ", data.O[tid].tolist())
        print('    Popt ', data.P[tid][np.argmin(data.O[tid])], 'Oopt ', min(data.O[tid])[0], 'nth ', np.argmin(data.O[tid]))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-nrun', type=int, help='Number of runs per task')
    args   = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    nrun = args.nrun
    ALITune(nrun)
