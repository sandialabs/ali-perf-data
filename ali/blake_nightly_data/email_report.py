# Import libraries
import datetime
import glob
import json
import numpy as np
import os
import sys

# Import scripts
from html2email import html2email
sys.path.insert(0,'kcshan-perf-analysis')
from email_report import changepoint_test

###################################################################################################
def simple_perf_test(wtimes, stdCoeff = 2.0):
    '''
    Simple performance test
    Returns:
        status, measured, mean, std
    Status:
        'pass' if test is within 2 standard deviations of the mean
        'warn' if the above is false but the previous test passes  (This is done to avoid spikes)
        'fail' otherwise
    '''
    # Compute mean and std
    wt = np.asarray(wtimes, dtype=np.float64)
    mu = np.mean(wt)
    sig = np.std(wt)

    # Performance test
    if wt[-1] - mu < stdCoeff*sig:
        status = 'pass'
    elif wt[-2] - mu < stdCoeff*sig:
        status = 'warn'
    else:
        status = 'fail'
    return status, wt[-1], mu, sig

###################################################################################################
def build_perf_tests(files, cases, nps, timers, metadata):
    '''
    Returns dictionary with performance tests
    '''
    sender = 'jwatkin@sandia.gov'
    recipients = ['jwatkin@sandia.gov','ikalash@sandia.gov']
    #recipients = ['jwatkin@sandia.gov']

    # If today's json file doesn't exist, send error message
    date = datetime.datetime.today().strftime('%Y%m%d')
    filesWithDate = [filename for filename in files if date in filename]
    if not filesWithDate:
        print("Today's json doesn't exist, sending error email...")
        html2email('[ALIPerfTestsFailed] Albany Land Ice Performance Tests - Blake',
                '''
                <b>Error: Today's json file doesn't exist!</b>
                <br><br>
                Click <a href="https://sems-cdash-son.sandia.gov/sems/index.php?project=Albany&filtercount=1&showfilters=1&field1=buildname&compare1=61&value1=blake-serial-sfad-Albany-PerfTests">here</a> for test logs and
                <a href="https://github.com/ikalash/ikalash.github.io/tree/master/ali/blake_nightly_data">here</a> for the repo.
                ''',
                sender, recipients)
        sys.exit()

    # Open today's json file
    latestFile = filesWithDate[0]
    with open(latestFile) as jf:
        ctestData = json.load(jf)

    # If today's json file is empty, send error message
    if not ctestData:
        print("Today's json is empty, sending error email...")
        html2email('[ALIPerfTestsFailed] Albany Land Ice Performance Tests - Blake',
                '''
                <b>Error: Today's json file is empty!</b>
                <br><br>
                Click <a href="https://sems-cdash-son.sandia.gov/sems/index.php?project=Albany&filtercount=1&showfilters=1&field1=buildname&compare1=61&value1=blake-serial-sfad-Albany-PerfTests">here</a> for test logs and
                <a href="https://github.com/ikalash/ikalash.github.io/tree/master/ali/blake_nightly_data">here</a> for the repo.
                ''',
                sender, recipients)
        sys.exit()

    # Determine status of today's tests before running performance tests
    perfTests = {}
    allPerfTestsFailedToRun = True
    for case in cases:
        name = case + '_np' + str(nps)
        perfTests[name] = {}
        perfTestsCaseDict = perfTests[name]

        if name in ctestData:
            if ctestData[name]['passed']:
                perfTestsCaseDict['runTest'] = 'Passed'
                perfTestsCaseDict['runTestColor'] = 'green'
                allPerfTestsFailedToRun = False

            # Failed test
            else:
                perfTestsCaseDict['runTest'] = 'Failed'
                perfTestsCaseDict['runTestColor'] = 'red'
                perfTestsCaseDict['perfTests'] = 'Failed'
                perfTestsCaseDict['perfTestsColor'] = 'red'

        # Failed test
        else:
            perfTestsCaseDict['runTest'] = 'Failed'
            perfTestsCaseDict['runTestColor'] = 'red'
            perfTestsCaseDict['perfTests'] = 'Failed'
            perfTestsCaseDict['perfTestsColor'] = 'red'

    # If today's performance tests are empty, send error message
    if allPerfTestsFailedToRun:
        print("Today's json doesn't have any performance tests, sending error email...")
        html2email('[ALIPerfTestsFailed] Albany Land Ice Performance Tests - Blake',
                '''
                <b>Error: All performance tests failed to run!</b>
                <br><br>
                Click <a href="https://sems-cdash-son.sandia.gov/sems/index.php?project=Albany&filtercount=1&showfilters=1&field1=buildname&compare1=61&value1=blake-serial-sfad-Albany-PerfTests">here</a> for test logs and
                <a href="https://github.com/ikalash/ikalash.github.io/tree/master/ali/blake_nightly_data">here</a> for the repo.
                ''',
                sender, recipients)
        sys.exit()

    # Initialize metrics lists
    metrics = {}
    for name,perfTestsCaseDict in perfTests.items():
        if perfTestsCaseDict['runTest'] == 'Failed':
            continue

        metrics[name] = {}
        for timer in timers:
            metrics[name][timer] = []
        for data in metadata:
            metrics[name][data] = []

    # Loop over files and construct list of metrics for performance testing
    for filename in files:
        # Load ctest data
        with open(filename) as jf:
            ctestData = json.load(jf)

        # Loop over timers
        for name,metricsCaseDict in metrics.items():
            if name in ctestData:
                if ctestData[name]['passed']:
                    for metric,metricList in metricsCaseDict.items():
                        if metric in ctestData[name]['timers']:
                            metricList.append(ctestData[name]['timers'][metric])
                        elif metric in ctestData[name]:
                            metricList.append(ctestData[name][metric])

    # Run performance tests
    colorMap = {'pass':'green','warn':'yellow','fail':'red'}
    for name,metricsCaseDict in metrics.items():
        perfTestsCaseDict = perfTests[name]
        
        # Test metrics
        perfTestsCaseDict['metrics'] = {}
        perfTestsMetricsDict = perfTestsCaseDict['metrics']
        colorCounter = {'green':0,'yellow':0,'red':0}
        for metric,metricList in metricsCaseDict.items():
            # Skip this test if metric list is empty
            if not metricList:
                continue

            perfTestsMetricsDict[metric] = {}
            perfTestsMetricDict = perfTestsMetricsDict[metric]
            perfStatus, perfTestsMetricDict['measured'], perfTestsMetricDict['mean'], perfTestsMetricDict['std'] = changepoint_test(metricList)

            # Extract performance test status
            color = colorMap[perfStatus]
            perfTestsMetricDict['perfTestColor'] = color
            colorCounter[color] = colorCounter[color] + 1

        # Extract overall performance tests status
        perfTestsCaseDict['perfTests'] = '{}/{}/{}'.format(colorCounter['green'],colorCounter['yellow'],colorCounter['red'])
        if colorCounter['red']:
            perfTestsCaseDict['perfTestsColor'] = 'red'
        elif colorCounter['yellow']:
            perfTestsCaseDict['perfTestsColor'] = 'yellow'
        else:
            perfTestsCaseDict['perfTestsColor'] = 'green'

    return perfTests

###################################################################################################
def build_perf_tests_html(perfTests):
    '''
    Returns html string with performance status report
    '''
    # Styles
    style = '''
    <style>
        table,th,td
        {
            border: 2px solid black;
            text-align: center;
        }
        table
        {
            border-collapse: collapse;
            width: 90%;
        }
        th
        {
            color: white;
            background-color: gray;
        }
        td
        {
            height: 40px;
        }
        tr:nth-child(even)
        {
            background-color: #D0D0D0;
        }
        tr:nth-child(odd)
        {
            background-color: #F0F0F0;
        }
        #green
        {
            background-color: green;
            color: white;
        }
        #yellow
        {
            background-color: yellow;
        }
        #red
        {
            background-color: red;
            color: white;
        }
    </style>
    '''

    # Title
    title = '''
    <font size="+2"><b>Albany Land Ice Performance Status Report on Blake</b></font>
    <br><br>
    '''

    # Status Table
    statusTab = '''
    <table>
        <caption><font size="+2"><b>Status</b></font></caption>
        <tr>
            <th>Name</th>
            <th>Run Test</th>
            <th>Performance Tests (Passes/Warnings/Fails)</th>
        </tr>
    '''
    for name, info in perfTests.items():
        row = '''
        <tr>
            <td>{}</td>
            <td id="{}">{}</td>
            <td id="{}">{}</td>
        </tr>
        '''.format(name,info['runTestColor'],info['runTest'],info['perfTestsColor'],info['perfTests'])
        statusTab = statusTab + row
    statusTab = statusTab + '''
    </table>
    '''

    # Subject and Metrics Tables
    subjectTestsFailed = False
    metricTabs = ''
    for name, info in perfTests.items():
        if info['runTest'] == 'Failed':
            subjectTestsFailed = True
            metricTabs = metricTabs + '''
            <br><br>
            <font size="+1">{} test failed...</font>
            '''.format(name)
            continue
        else:
            metricTab = '''
            <br><br>
            <table>
                <caption><font size="+2"><b>{} timers (s) or memory (MiB)</b></font></caption>
                <tr>
                    <th>Metrics</th>
                    <th>Measured</th>
                    <th>Mean</th>
                    <th>Std</th>
                </tr>
            '''.format(name)
            for metric, metricInfo in info['metrics'].items():
                row = '''
                <tr>
                    <td>{}</td>
                    <td id="{}">{:g}</td>
                    <td>{:g}</td>
                    <td>{:g}</td>
                </tr>
                '''.format(metric,metricInfo['perfTestColor'],metricInfo['measured'],metricInfo['mean'],metricInfo['std'])
                metricTab = metricTab + row

                if metricInfo['perfTestColor'] == 'red':
                    subjectTestsFailed = True
            metricTab = metricTab + '''
            </table>
            '''
            metricTabs = metricTabs + metricTab
    subject = 'Albany Land Ice Performance Tests - Blake'
    if subjectTestsFailed:
        subject = '[ALIPerfTestsFailed] ' + subject
    else:
        subject = '[ALIPerfTestsPassed] ' + subject

    # Links
    date = datetime.datetime.today().strftime('%m_%d_%Y')
    testLogsLink = 'https://sems-cdash-son.sandia.gov/sems/index.php?project=Albany&filtercount=1&showfilters=1&field1=buildname&compare1=61&value1=blake-serial-sfad-Albany-PerfTests'
    notebookHtmlLink = 'https://ikalash.github.io/ali/blake_nightly_data/Ali_PerfTestsBlake_' + date + '.html'
    notebookLink = 'https://mybinder.org/v2/gh/ikalash/ikalash.github.io/master?filepath=ali/blake_nightly_data%2FAli_PerfTestsBlake.ipynb'
    links = '''
    <br>
    Click <a href="{}">here</a> for test logs, <a href="{}">here</a> for more details on performance or <a href="{}">here</a> for an interactive notebook of the data.
    '''.format(testLogsLink, notebookHtmlLink, notebookLink)

    return subject, style + title + statusTab + metricTabs + links

###################################################################################################
if __name__ == "__main__":
    '''
    Send email showing status report of performance tests
    '''
    # Email inputs
    sender = 'jwatkin@sandia.gov'
    recipients = ['jwatkin@sandia.gov','ikalash@sandia.gov','mperego@sandia.gov','lbertag@sandia.gov','kyleshan@stanford.edu','rstumin@sandia.gov','maxcarl@sandia.gov']
    #recipients = ['jwatkin@sandia.gov']

    # Pass directory name
    if len(sys.argv) < 2:
        dir = ''
    else:
        dir = sys.argv[1]

    # Extract file names
    files = sorted(glob.glob(os.path.join(dir,'ctest-*')))

    # Specify case to extract from ctest.json file
    cases = ('ant-2-20km_ml_ls',
             'ant-2-20km_mu_ls',
             'ant-2-20km_mu_dls',
             'green-1-7km_fea_1ws',
             'green-1-7km_mu_dls_1ws',
             'green-1-7km_fea_mem',
             'green-1-7km_ml_ls_mem',
             'green-1-7km_mu_ls_mem',
             'green-1-7km_mu_dls_mem',
             'green-1-7km_muk_ls_mem',
             'green-3-20km_beta_1ws',
             'green-3-20km_beta_mem',
             'green-3-20km_beta_memp')

    # Specify number of processes to extract from ctest.json file
    nps = 384

    # Specify timers to extract from ctest.json file (note: must be unique names per test in file)
    timers = ('Albany Total Time:',
              'Albany: Setup Time:',
              'Albany: Total Fill Time:',
              'Albany Fill: Residual:',
              'Albany Residual Fill: Evaluate:',
              'Albany Residual Fill: Export:',
              'Albany Fill: Jacobian:',
              'Albany Jacobian Fill: Evaluate:',
              'Albany Jacobian Fill: Export:',
              'NOX Total Preconditioner Construction:',
              'NOX Total Linear Solve:')

    # Specify metadata to extract from ctest.json file
    metadata = ('max host memory',
                'max kokkos memory')

    # Run performance tests and build dictionary
    print("Running performance analysis...")
    perfTests = build_perf_tests(files, cases, nps, timers, metadata)
    #print(perfTests)

    # Build html string
    print("Building HTML...")
    subject, perfTestsHTML = build_perf_tests_html(perfTests)
    #print(perfTestsHTML)

    # Email status report
    print("Sending email...")
    html2email(subject, perfTestsHTML, sender, recipients)

