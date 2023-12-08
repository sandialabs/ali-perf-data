from PyAlbany import Utils
import os
import sys
import argparse
from timeout import timeout

class PyAlbanyInstance:
    def __init__(self, filename, parallelEnv):
        self._parallelEnv = parallelEnv
        self._filename = filename
        self._problem = None
    def reportTimers(self):
        self._problem.reportTimers()
    def solve(self, tuningParameters, timelimit=500):

        @timeout(timelimit)
        def time_limited_solve():
            return self._problem.performSolve()

        # Get the problem's parameter list from PyAlbany
        parameters = Utils.createParameterList(filename, parallelEnv)

        # Get the sublist for ms1
        ms1 = parameters.sublist("Piro").sublist("NOX").sublist("Direction").sublist("Newton").sublist("Stratimikos Linear Solver").sublist("Stratimikos").sublist("Preconditioner Types").sublist("MueLu").sublist("Factories").sublist("mySmoother1")
        # Set the smoother parameters according to tuningParameters
        if tuningParameters[0] == 'MT_Gauss_Seidel':
            ms1.set('type', 'RELAXATION')
            pList = Utils.createEmptyParameterList()
            pList.set('relaxation: type',                     'Two-stage Gauss-Seidel')
            pList.set('relaxation: sweeps',                   tuningParameters[1])
            pList.set('relaxation: damping factor',           tuningParameters[2])
            ms1.set('ParameterList', pList)
        elif tuningParameters[0] == 'Two_stage_Gauss_Seidel':
            ms1.set('type', 'RELAXATION')
            pList = Utils.createEmptyParameterList()
            pList.set('relaxation: type',                     'Two-stage Gauss-Seidel')
            pList.set('relaxation: sweeps',                   tuningParameters[1])
            pList.set('relaxation: inner damping factor',     tuningParameters[3])
            ms1.set('ParameterList', pList)
        elif tuningParameters[0] == 'Chebyshev':
            ms1.set('type', 'CHEBYSHEV')
            pList = Utils.createEmptyParameterList()
            pList.set('chebyshev: degree',                    tuningParameters[4])
            pList.set('chebyshev: ratio eigenvalue',          tuningParameters[5])
            pList.set('chebyshev: eigenvalue max iterations', tuningParameters[6])
            ms1.set('ParameterList', pList)
        else:
            print("Invalid tuning paremeters, using default ms1.")

        # Get the sublist for ms4
        ms4 = parameters.sublist("Piro").sublist("NOX").sublist("Direction").sublist("Newton").sublist("Stratimikos Linear Solver").sublist("Stratimikos").sublist("Preconditioner Types").sublist("MueLu").sublist("Factories").sublist("mySmoother4")
        # Set the smoother parameters according to tuningParameters
        if tuningParameters[7] == 'MT_Gauss_Seidel':
            ms4.set('type', 'RELAXATION')
            pList = Utils.createEmptyParameterList()
            pList.set('relaxation: type',                     'Two-stage Gauss-Seidel')
            pList.set('relaxation: sweeps',                   tuningParameters[8])
            pList.set('relaxation: damping factor',           tuningParameters[9])
            ms4.set('ParameterList', pList)
        elif tuningParameters[7] == 'Two_stage_Gauss_Seidel':
            ms4.set('type', 'RELAXATION')
            pList = Utils.createEmptyParameterList()
            pList.set('relaxation: type',                     'Two-stage Gauss-Seidel')
            pList.set('relaxation: sweeps',                   tuningParameters[8])
            pList.set('relaxation: inner damping factor',     tuningParameters[10])
            ms4.set('ParameterList', pList)
        elif tuningParameters[7] == 'Chebyshev':
            ms4.set('type', 'CHEBYSHEV')
            pList = Utils.createEmptyParameterList()
            pList.set('chebyshev: degree',                    tuningParameters[11])
            pList.set('chebyshev: ratio eigenvalue',          tuningParameters[12])
            pList.set('chebyshev: eigenvalue max iterations', tuningParameters[13])
            ms4.set('ParameterList', pList)
        else:
            print("Invalid tuning paremeters, using default ms4.")

        # DEBUG: Print smoother parameterLists
        if parallelEnv.getComm().getRank() == 0:
            print(ms1)
            print(ms4)
        parallelEnv.getComm().barrier()

        # Create and solve problem
        self._problem = Utils.createAlbanyProblem(parameters, parallelEnv)
        try:
            converged = time_limited_solve()
        except:
            converged = 1

        # Get timing information for performSolve
        stackedTimer = self._problem.getStackedTimer()
        solve_time = stackedTimer.accumulatedTime("PyAlbany: performSolve")

        if converged:
            solve_time = 1e12

        return solve_time

def parse_args():

    parser = argparse.ArgumentParser()

    # Parameters
    parser.add_argument('-ms1_smoother_name', type=str, default="MT_Gauss_Seidel", help='')
    parser.add_argument('-ms1_relaxation_num_sweeps', type=int, default=5, help='')
    parser.add_argument('-ms1_relaxation_damping_factor', type=float, default=0.75, help='')
    parser.add_argument('-ms1_relaxation_inner_damping_factor', type=float, default=1.25, help='')
    parser.add_argument('-ms1_chebyshev_degree', type=int, default=1, help='')
    parser.add_argument('-ms1_chebyshev_eig_ratio', type=float, default=3.14, help='')
    parser.add_argument('-ms1_chebyshev_max_iters', type=int, default=20, help='')
    parser.add_argument('-ms4_smoother_name', type=str, default="MT_Gauss_Seidel", help='')
    parser.add_argument('-ms4_relaxation_num_sweeps', type=int, default=5, help='')
    parser.add_argument('-ms4_relaxation_damping_factor', type=float, default=0.75, help='')
    parser.add_argument('-ms4_relaxation_inner_damping_factor', type=float, default=1.25, help='')
    parser.add_argument('-ms4_chebyshev_degree', type=int, default=1, help='')
    parser.add_argument('-ms4_chebyshev_eig_ratio', type=float, default=3.14, help='')
    parser.add_argument('-ms4_chebyshev_max_iters', type=int, default=20, help='')

    # Constant settings
    parser.add_argument('-populate', type=bool, default=False, help='')

    # Job info
    parser.add_argument('-mesh', type=str, default="humboldt-3-20km", help='')
    parser.add_argument('-input', type=str, default='.', help='')
    parser.add_argument('-output', type=str, default='solvetime.txt', help='')

    parser.add_argument('-timelimit', type=int, default=500, help='')

    args = parser.parse_args()

    return args

if __name__ == "__main__":

    global POPULATE
    global MESH
    global DATAPATH
    global OUTPATH
    global TIMEOUT

    # input format: ['smoother name', 'relaxation: sweeps', 'relaxation: damping factor',
    #                'relaxation: inner damping factor', 'chebyshev: degree',
    #                'chebyshev: ratio eigenvalue', 'chebyshev: eigenvalue max iterations']

    # Parse command line arguments
    args = parse_args()
    POPULATE = args.populate
    MESH = args.mesh
    DATAPATH = args.input
    OUTPATH = args.output
    tuningParameters = []
    tuningParameters.append(args.ms1_smoother_name)
    tuningParameters.append(args.ms1_relaxation_num_sweeps)
    tuningParameters.append(args.ms1_relaxation_damping_factor)
    tuningParameters.append(args.ms1_relaxation_inner_damping_factor)
    tuningParameters.append(args.ms1_chebyshev_degree)
    tuningParameters.append(args.ms1_chebyshev_eig_ratio)
    tuningParameters.append(args.ms1_chebyshev_max_iters)
    tuningParameters.append(args.ms4_smoother_name)
    tuningParameters.append(args.ms4_relaxation_num_sweeps)
    tuningParameters.append(args.ms4_relaxation_damping_factor)
    tuningParameters.append(args.ms4_relaxation_inner_damping_factor)
    tuningParameters.append(args.ms4_chebyshev_degree)
    tuningParameters.append(args.ms4_chebyshev_eig_ratio)
    tuningParameters.append(args.ms4_chebyshev_max_iters)

    TIMEOUT = args.timelimit

    # initialize
    comm = Utils.getDefaultComm()
    parallelEnv = Utils.createDefaultParallelEnv(comm)

    # report solve times
    if comm.getRank() == 0:
        with open(OUTPATH, 'w') as file:
            file.write(str(1e12))
    comm.barrier()

    # populate mesh
    if POPULATE:
        filename = DATAPATH + "/problems/" + MESH + "/input_albany_PopulateMesh_Wedge.yaml"
        problem = Utils.createAlbanyProblem(filename, parallelEnv)
        problem.performSolve()
        problem = None

    # set up pyalbany instance
    filename = DATAPATH + "/problems/" + MESH + "/input_albany_Velocity_MueLuKokkos_Wedge.yaml"
    solver = PyAlbanyInstance(filename, parallelEnv)

    # run experiment
    solve_time = solver.solve(tuningParameters, timelimit=TIMEOUT)
    solver.reportTimers()

    # report solve times
    if comm.getRank() == 0:
        print("Solve time:", solve_time)
        with open(OUTPATH, 'w') as file:
            file.write(str(solve_time))
    comm.barrier()

    # cleanup
    solver = None
    problem = None
    parallelEnv = None
    comm = None

