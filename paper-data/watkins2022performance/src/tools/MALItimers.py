# Import libraries
import json
import warnings

###################################################################################################
def MALItimers(landice_info = {}, albany_info = {}):
    '''
    Extract timer data from MALI log files
    '''
    # Print all warnings
    warnings.simplefilter("always")

    # Force warnings.warn() to omit the source code line in the message
    formatwarning_orig = warnings.formatwarning
    warnings.formatwarning = lambda message, category, filename, lineno, line=None: \
                formatwarning_orig(message, category, filename, lineno, line='')

    timer_data = {}

    # Extract information from landice timer file
    if landice_info:
        wtimes = {}
        filename = landice_info['file']
        timers = landice_info['timers']
        wtimeAvgLoc = 4
        with open(filename, 'r') as f:
            for line in f:
                for name, timer in timers.items():
                    if timer in line:
                        wtimes[name] = wtimes.get(name, 0) + float(line.split(timer)[1].split()[wtimeAvgLoc])

        # Check if timer data is empty
        if not wtimes:
            warnings.warn('Parsing of '+filename+' failed. Check to see if inputs are valid.', Warning)

        # Fill empty data with nans
        for name, timer in timers.items():
            if name not in wtimes:
                warnings.warn(timer + ' not found in '+filename+'! Setting name to nan.', Warning)
                wtimes[name] = float('nan')
        timer_data.update(wtimes)


    # Extract information from albany timer file
    if albany_info:
        wtimes = {}
        filename = albany_info['file']
        timers = albany_info['timers']
        wtimeAvgLoc = 0
        with open(filename, 'r') as f:
            for line in f:
                for name, timer in albany_info['timers'].items():
                    if timer in line:
                        wtimes[name] = wtimes.get(name, 0) + float(line.split(timer)[1].split()[wtimeAvgLoc].replace(',',''))

        # Check if timer data is empty
        if not wtimes:
            warnings.warn('Parsing of '+filename+' failed. Check to see if inputs are valid.', Warning)

        # Fill empty data with nans
        for name, timer in timers.items():
            if name not in wtimes:
                warnings.warn(timer + ' not found in '+filename+'! Setting name to nan.', Warning)
                wtimes[name] = float('nan')
        timer_data.update(wtimes)

    return timer_data

###################################################################################################
if __name__ == "__main__":
    '''
    Example: import log.albany.timers.out and log.landice.timers.out files and print timer data
    '''
    # Extract file names
    landice_info = {}
    landice_info['file'] = 'log.landice.timers.out'
    albany_info = {}
    albany_info['file'] = 'log.albany.timers.out'

    # Specify timers to extract from files (note: must be unique names)
    landice_info['timers'] = {}
    timers = landice_info['timers']
    timers['MALI Total Time'] =      '1 total time'
    timers['MALI Velocity Solve'] =  '4    velocity solve'
    timers['MALI Extrude 3D Grid'] = '5     velocity_solver_extrude_3d_grid'
    timers['MALI SolveFO'] =         '5     velocity_solver_solve_FO'
    albany_info['timers'] = {}
    timers = albany_info['timers']
    timers['Albany Total Time'] =           'Albany Velocity Solver:'
    timers['Albany Extrude 3D Grid'] =      'Albany: Extrude 3D Grid:'
    timers['Albany SolveFO'] =              'Albany: SolveFO:'
    timers['Total Fill'] =                  'Albany: Total Fill Time:'
    timers['Fill: Residual'] =              'Albany Fill: Residual:'
    timers['Residual Fill: Evaluate'] =     'Albany Residual Fill: Evaluate:'
    timers['Residual Fill: Export'] =       'Albany Residual Fill: Export:'
    timers['Fill: Jacobian'] =              'Albany Fill: Jacobian:'
    timers['Jacobian Fill: Evaluate'] =     'Albany Jacobian Fill: Evaluate:'
    timers['Jacobian Fill: Export'] =       'Albany Jacobian Fill: Export:'
    timers['Preconditioner Construction'] = 'NOX Total Preconditioner Construction:'
    timers['Linear Solve'] =                'NOX Total Linear Solve:'

    # Extract info
    print(json.dumps(MALItimers(), sort_keys=False, indent=2))
    print(json.dumps(MALItimers(landice_info=landice_info), sort_keys=False, indent=2))
    print(json.dumps(MALItimers(albany_info=albany_info), sort_keys=False, indent=2))
    print(json.dumps(MALItimers(landice_info, albany_info), sort_keys=False, indent=2))

