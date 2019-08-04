# Import libraries
import glob
import json
import os
import sys

###################################################################################################
def json2strong(file, case, timer):
    '''
    Extract number of processes and wall-clock times (s) from ctest.json file
    '''
    # Load ctest data
    with open(file) as jf:
        ctestData = json.load(jf)

    # Organize data for strong scaling plots
    nps = []
    wtimes = []
    for ctest in ctestData.values():
        if ctest['case'] == case:
            if timer in ctest['timers']:
                nps.append(ctest['np'])
                wtimes.append(ctest['timers'][timer])

    # Sort based on number of processes
    nps, wtimes = zip(*sorted(zip(nps, wtimes)))

    return nps, wtimes

###################################################################################################
if __name__ == "__main__":
    '''
    Example: Load dummy json and test extraction of strong scaling data
    '''
    # Pass directory name
    if len(sys.argv) < 2:
        dir = ''
    else:
        dir = sys.argv[1]

    # Extract file names
    files = glob.glob(os.path.join(dir,'ctest-*'))

    # Specify case to extract from ctest.json file
    cases = ('R0','R1')

    # Specify timers to extract from ctest.json file (note: must be unique names per test in file)
    timers = ('panzer::ModelEvaluator::evalModel(J):',
              'Stratimikos: BelosLOWS:',
              'GMRES block system: Operation Prec*x:',
              'CG S_E: BlockCGSolMgr total solve time:')

    # Loop over files for this example
    for file in files:
        for case in cases:
            for timer in timers:
                # Extract info and print
                nps, wtimes = json2strong(file, case, timer)
                print(nps,wtimes)

