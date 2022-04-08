# Import libraries
import glob
import json
import os
import sys
import datetime as dt
import pandas as pd

###################################################################################################
def json2dataframe(files, cases, names, timers, metrics, metadata):
    '''
    Extract timer data from json files and output as pandas DataFrame
    Inputs:
        files   : List of .json files
        cases   : List of test cases WITH np
        names   : Presentable names of timers
        timers  : Raw names of timers
        metrics : Additional performance metrics
        metadata: Additional fields to add to metrics
    '''
    output = {}
    output['case'] = []
    output['date'] = []
    for meta in metadata:
        output[meta] = []
    for name in names:
        output[name] = []
    for metric in metrics:
        output[metric] = []
        
    for file in files:
        with open(file) as jf:
            ctest_data = json.load(jf)
        for case in cases:
            if case in ctest_data.keys():
                info = ctest_data[case]
                if not info['passed']:
                    continue
                output['case'].append(case)
                output['date'].append(dt.datetime.strptime(str(info['date']), '%Y%m%d'))
                for meta in metadata:
                    output[meta].append(info.get(meta))
                for name, timer in zip(names, timers):
                    output[name].append(info['timers'].get(timer))
                for metric in metrics:
                    output[metric].append(info.get(metric))
                    
    output_df = pd.DataFrame(output)
    output_df.sort_values(by=['date', 'case'], inplace=True)
    return output_df


###################################################################################################
if __name__ == "__main__":
    '''
    Example: Load json and test extraction of dataframe
    '''
    # Pass directory name
    if len(sys.argv) < 2:
        dr = ''
    else:
        dr = sys.argv[1]

    # Extract file names
    files = glob.glob(os.path.join(dr,'ctest-*'))

    # Specify case to extract from ctest.json file
    cases = (
        'green-1-7km_muk_ls_mem_np8',
        'green-3-20km_vel_muk_wdg_np8'
    )

    # Specify presentable names of timers
    names = (
        'Total Time',
        'Setup Time',
        'Total Fill Time',
        'Total Prec Time',
        'Total LinSol Time'
    )

    # Specify timers to extract from ctest.json file (note: must be unique names per test in file)
    timers = (
        'Albany Total Time:',
        'Albany: Setup Time:',
        'Albany: Total Fill Time:',
        'NOX Total Preconditioner Construction:',
        'NOX Total Linear Solve:'
    )

    # Specify additional metrics
    metrics = (
        'max host memory',
        'max kokkos memory'
    )

    # Specify metadata
    metadata = (
        'Albany cxx compiler',
        'Albany git commit id',
        'Trilinos git commit id'
    )
        

    # Extract dataframe and print
    df = json2dataframe(files, cases, names, timers, metrics, metadata)
    print(df)

