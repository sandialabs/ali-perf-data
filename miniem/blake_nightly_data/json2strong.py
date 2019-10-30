# Import libraries
import glob
import json
import os
import sys
import warnings

###################################################################################################
def json2strong(file, case, timer, warn = True):
    '''
    Extract number of processes and wall-clock times (s) from ctest.json file
    '''
    # Print all warnings
    warnings.simplefilter("always")

    # Force warnings.warn() to omit the source code line in the message
    formatwarning_orig = warnings.formatwarning
    warnings.formatwarning = lambda message, category, filename, lineno, line=None: \
                formatwarning_orig(message, category, filename, lineno, line='')

    # Load ctest data
    with open(file) as jf:
        ctestData = json.load(jf)

    # Organize data for strong scaling plots
    nps = []
    wtimes = []
    for name,info in ctestData.items():
        if info['case'] == case:
            if timer in info['timers']:
                nps.append(info['np'])
                wtimes.append(info['timers'][timer])
            elif warn:
                warnings.warn(timer + ' not found in '+name+', '+file+'!',Warning)

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

