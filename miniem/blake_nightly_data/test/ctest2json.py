# Import libraries
import glob
import json
import os
import sys
import warnings

###################################################################################################
def ctest2json(file, allTimers):
    '''
    Extract information from ctest output file and load into json file
    '''
    # Print all warnings
    warnings.simplefilter("always")

    # Force warnings.warn() to omit the source code line in the message
    formatwarning_orig = warnings.formatwarning
    warnings.formatwarning = lambda message, category, filename, lineno, line=None: \
                formatwarning_orig(message, category, filename, lineno, line='')

    # ctest file specific information
    testNameKey = ' Test: '
    testNameLoc = 2
    wtimeAvgLoc = 0
    wtimeCallsLoc = 3
    testPassedKey = 'Test Passed'
    testFailedKey = 'Test Failed'

    # Extract information from ctest file
    ctestInfo = {}
    testName = ''
    timers = list()
    with open(file, 'r') as f:
        for line in f:
            # Extract test information
            if testNameKey in line:
                # Init test info
                testName = line.split()[testNameLoc]
                ctestInfo[testName] = {}
                ctestInfo[testName]['case'] = testName.split('_')[2]
                ctestInfo[testName]['np'] = int(testName.split('_')[3][2:])
                ctestInfo[testName]['date'] = int(file.split('_')[1].split('-')[0])

                # Init list of timers
                timers = list(allTimers)
                ctestInfo[testName]['timers'] = {}

            # Extract timer information
            for timer in timers:
                if timer in line:
                    wtime = float(line.split(timer)[1].split()[wtimeAvgLoc])
                    calls = int(line.split(timer)[1].split()[wtimeCallsLoc].strip('[]'))
                    ctestInfo[testName]['timers'][timer] = wtime / calls

                    # Remove timer from list
                    timers.remove(timer)
                    break

            # Extract pass
            if testPassedKey in line:
                ctestInfo[testName]['passed'] = True

            # Extract fail
            if testFailedKey in line:
                ctestInfo[testName]['passed'] = False
                warnings.warn(testName+', '+file+' failed! Timers are not stored.', Warning)


    # Check if ctest data is empty
    if not ctestInfo:
        raise RuntimeError('Parsing of '+file+' failed. Check to see if testNameKey is valid.')

    # Check to see if test timers were captured
    timersCaptured = 0
    for name,info in ctestInfo.items():
        if info['timers']:
            timersCaptured = timersCaptured+1

        if info['passed'] and not info['timers']:
            ctestInfo[testName]['passed'] = False
            warnings.warn(name+', '+file+' passed but parsing of timers failed. Setting test to failed.', Warning)

    # If timers were not captured in any tests, the timers might not be valid
    if timersCaptured == 0:
        raise RuntimeError('Parsing of timers failed for '+file+'. Check to see if timers are valid.')

    # Add date and save to json file
    date = file.split('_')[1].split('-')[0]
    jsonFile = 'ctest-' + date + '.json'
    with open(jsonFile, 'w') as jf:
        json.dump(ctestInfo, jf)

###################################################################################################
if __name__ == "__main__":
    '''
    Import LastTest_* files and convert to json
    '''
    # Pass directory name
    if len(sys.argv) < 2:
        dir = ''
    else:
        dir = sys.argv[1]
        print('Converting ctest files in ' + dir + ' to json...')

    # Extract file names
    files = glob.glob(os.path.join(dir,'LastTest_*'))

    # Specify timers to extract from ctest file (note: must be unique names per test in file)
    timers = ('panzer::ModelEvaluator::evalModel(J):',
              'Stratimikos: BelosLOWS:',
              'GMRES block system: Operation Prec*x:',
              'CG S_E: BlockCGSolMgr total solve time:')

    # Loop over files
    for file in files:
        # Extract info and save in json file
        ctest2json(file, timers)

