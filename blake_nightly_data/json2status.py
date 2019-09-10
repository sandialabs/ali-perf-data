# Import libraries
import glob
import json
import os
import sys

###################################################################################################
def json2status(files, case, np):
    '''
    Extract dates and wall-clock times (s) from ctest.json files
    '''
    dates = []
    status = []
    for file in files:
        # Load ctest data
        with open(file) as jf:
            ctestData = json.load(jf)

        # Organize data for strong scaling plots
        for name,info in ctestData.items():
            if info['case'] == case and info['np'] == np:
                dates.append(info['date'])
                status.append(info['passed'])

    # Sort based on dates
    dates, status = zip(*sorted(zip(dates, status)))

    return dates, status

###################################################################################################
if __name__ == "__main__":
    '''
    Example: Load dummy json and test extraction of status data
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

    # Specify number of processes to extract from ctest.json file
    nps = {'R0': (48, 96, 192, 384), 'R1': (384, 768)}

    # Loop over cases for this example
    for case in cases:
        for np in nps[case]:
            # Extract info and print
            dates, status = json2status(files, case, np)
            print(dates,status)

