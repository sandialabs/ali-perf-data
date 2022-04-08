# Import libraries
import json
import warnings

###################################################################################################
def MALIiters(filename):
    '''
    Extract iteration data from MALI log files
    '''
    # Print all warnings
    warnings.simplefilter("always")

    # Force warnings.warn() to omit the source code line in the message
    formatwarning_orig = warnings.formatwarning
    warnings.formatwarning = lambda message, category, filename, lineno, line=None: \
                formatwarning_orig(message, category, filename, lineno, line='')

    # Extract information from albany timer file
    iter_data = {}
    linsol_key = 'NOX Total Linear Solve:'
    liniter_key = 'Belos: Operation Prec*x:'
    with open(filename, 'r') as f:
        for line in f:
            # Extract nonlinear iterations and linsol time
            if linsol_key in line:
                iter_data['Nonlinear Iterations'] = int(line.split(linsol_key)[1].split('[')[1].split(']')[0])
                iter_data['Total Linear Solve Time'] = float(line.split(linsol_key)[1].split()[0].replace(',',''))

            # Extract linear iterations and preconditioner apply time
            if liniter_key in line:
                iter_data['Linear Iterations'] = int(line.split(liniter_key)[1].split('[')[1].split(']')[0])
                iter_data['Total Preconditioner Apply Time'] = float(line.split(liniter_key)[1].split()[0].replace(',',''))

    # Check if timer data is empty
    if not iter_data:
        warnings.warn('Parsing of '+filename+' failed. Check to see if inputs are valid.', Warning)

    return iter_data

###################################################################################################
if __name__ == "__main__":
    '''
    Example: import log.albany.timers.out files and print iteration data
    '''
    # Extract info
    filename = 'log.albany.timers.out'
    print(json.dumps(MALIiters(filename), sort_keys=False, indent=2))

