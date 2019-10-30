# Import libraries
import glob
import json
import os
import sys
import warnings

###################################################################################################
def json2timeline(files, case, np, timer, warn = True):
    '''
    Extract dates and wall-clock times (s) from ctest.json files
    '''
    # Print all warnings
    warnings.simplefilter("always")

    # Force warnings.warn() to omit the source code line in the message
    formatwarning_orig = warnings.formatwarning
    warnings.formatwarning = lambda message, category, filename, lineno, line=None: \
                formatwarning_orig(message, category, filename, lineno, line='')

    dates = []
    wtimes = []
    for file in files:
        # Load ctest data
        with open(file) as jf:
            ctestData = json.load(jf)

        # Organize data for strong scaling plots
        for name,info in ctestData.items():
            if info['case'] == case and info['np'] == np:
                date = info['date']
                dates.append(date)
                if timer in info['timers']:
                    wtimes.append(info['timers'][timer])
                elif warn:
                    warnings.warn(timer + ' not found in '+name+', '+file+'!', Warning)

    # Sort based on dates
    if wtimes:
        dates, wtimes = zip(*sorted(zip(dates, wtimes)))

    return dates, wtimes

###################################################################################################
if __name__ == "__main__":
    '''
    Example: Load dummy json and test extraction of timeline data
    '''
    # Pass directory name
    if len(sys.argv) < 2:
        dir = ''
    else:
        dir = sys.argv[1]

    # Extract file names
    files = glob.glob(os.path.join(dir,'ctest-*'))

    # Specify case to extract from ctest.json file
    cases = ('ant-2-20km_ml_line','ant-2-20km_muelu_line','ant-2-20km_muelu_decoupled_line')

    # Specify number of processes to extract from ctest.json file
    np = 384

    # Specify timers to extract from ctest.json file (note: must be unique names per test in file)
    timers = ('Albany: Total Time:',
              'Albany: **Total Fill Time**:',
              'NOX Total Preconditioner Construction:',
              'NOX Total Linear Solve:')

    # Loop over cases for this example
    for case in cases:
        for timer in timers:
            # Extract info and print
            dates, wtimes = json2timeline(files, case, np, timer)
            print(dates,wtimes)

