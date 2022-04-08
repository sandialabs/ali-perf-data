# Import libraries
import glob
import json
import matplotlib.pyplot as plt
import numpy as np
import sys

# Import functions
sys.path.insert(0,'src/changepoint')
from trimmed_test import trim
from trimmed_test import trimmed_ttest
from trimmed_test import trimmed_ttest_bounds
from trimmed_test import trimmed_bounds
sys.path.insert(0,'src/tools')
from MALIiters import MALIiters
from MALItimers import MALItimers
from BarStackGroups import plotBarStackGroups

# Set fontsize and plotting text to latex
plt.rc('text', usetex=True)
plt.rc('font', family='serif', size=18)

###################################################################################################
def ReportPerformanceProfiles(timers_data, total_time_data):
    '''
     - Compute mean proportions of 'Total Time'
     - Construct a series of barplots to highlight bottlenecks
    '''
    # Get sizes for matrix
    num_timers = len(timers_data)
    num_archs = len(total_time_data)
    num_cases = len(next(iter(total_time_data.values())))

    # Compute mean proportions
    props = np.zeros((num_archs, num_cases, num_timers))
    for k, arch_data in enumerate(timers_data.values()):
        for i, (case_data, total_case_data) in enumerate(zip(arch_data.values(), total_time_data.values())):
            for j, (wtimes, total_wtimes) in enumerate(zip(case_data.values(), total_case_data.values())):
                props[i,j,k] = np.sum(np.divide(np.array(wtimes), np.array(total_wtimes))) / len(wtimes)
    #print(props)

    colors = (
        (0/255, 128/255, 128/255), # teal
        (128/255, 0/255, 128/255), # purple
        (255/255, 192/255, 203/255)) # pink
    textstr = r'''\underline{Cases}
                 $a$: Baseline
                 $b$: Improvement'''

    # Plot results
    fig = plt.figure(figsize=(14,8))
    Groups = list(total_time_data.keys())
    Stacks = (('$a$','$b$'),('$a$','$b$'),('$a$','$b$'),('$a$','$b$'))
    Timers = list(timers_data.keys())
    h = plotBarStackGroups(props, Groups, Stacks, colors)
    plt.ylabel('Proportions')
    plt.ylim((0, 1.0))
    eles = []
    for i in range(num_timers):
        eles += [h[0][i][0]]
    leg = plt.legend(eles, Timers, bbox_to_anchor=(1.04,1), borderaxespad=0, title=r'\underline{Timers}')
    leg._legend_box.align = "left"
    plt.tight_layout()
    ax = plt.gca()
    ax.set_axisbelow(True)
    ax.grid(linestyle='--', alpha=0.5)

    # Add Configurations
    tabXPos = 0.714
    tabYPos = 0.60
    plt.gcf().text(tabXPos, tabYPos, textstr,
            bbox=dict(boxstyle='round,pad=0.5',facecolor='none',edgecolor='black',linewidth=1.0,alpha=0.2))
    plt.subplots_adjust(right=0.68)
    plt.show()


###################################################################################################
def ReportPerformanceImprovements(timer_data, color_data):
    '''
     - Test to determine if performance improvement is statistically significant
     - Construct a series of boxplots to show performance improvements
    '''
    # Boxplots
    fig = plt.figure(figsize=(8,8))
    xticks = []
    for i, (gname, cases) in enumerate(timer_data.items()):
        num_cases = len(cases.keys())
        xticks.append(i * num_cases + 1 + 0.5 * (num_cases - 1))
        for j, (case, wtimes) in enumerate(cases.items()):
            # Barplot
            pos = [i * num_cases + (j + 1),]
            bp = plt.boxplot(wtimes, positions=pos, widths=0.9, patch_artist=True, whis=[0,100], showcaps=False)
            
            # Change color
            boxlinecolor = color_data[case]['boxlinecolor']
            bp['medians'][0].set(color=boxlinecolor, linewidth=2.0)
            bp['whiskers'][0].set(color=boxlinecolor, linewidth=2.0, linestyle='--')
            bp['whiskers'][1].set(color=boxlinecolor, linewidth=2.0, linestyle='--')
            bp['boxes'][0].set(color=boxlinecolor, linewidth=2.0)
            boxfacecolor = color_data[case]['boxfacecolor']
            bp['boxes'][0].set_facecolor(boxfacecolor)

            # Mean errorbar for small sample size
            errlinecolor = color_data[case]['errlinecolor']
            logt = np.log(wtimes)
            logt_mean, logt_lower, logt_upper = trimmed_bounds(logt)
            t_mean, t_lower, t_upper = np.exp(logt_mean), np.exp(logt_lower), np.exp(logt_upper)
            t_error = [[t_mean - t_lower], [t_upper - t_mean]]
            plt.errorbar(pos, t_mean, yerr=t_error, fmt='s', color=errlinecolor, zorder=10, elinewidth=2, capsize=8, capthick=2)

            # Plot trimmed outliers
            logt_trimmed, logt_outliers = trim(logt, outliers=True)
            t_outliers = np.exp(logt_outliers)
            plt.plot([pos]*len(t_outliers), t_outliers, linestyle='None', marker='o', markeredgecolor=errlinecolor, markeredgewidth=2, markerfacecolor='None', zorder=10)

    # Legend
    num_cases = len(color_data)
    cases = list(color_data.keys())
    legend_markers = []
    for case, color in color_data.items():
        boxlinecolor = color['boxlinecolor']
        boxfacecolor = color['boxfacecolor']
        errlinecolor = color_data[case]['errlinecolor']
        h = plt.errorbar(xticks[-1]+3.0, t_mean, yerr=[[1], [1]], fmt='s', color=errlinecolor, elinewidth=2, capsize=8, capthick=2, visible='off')
        legend_markers.append(h)
    plt.legend(legend_markers, cases, bbox_to_anchor=(0, 1.02, 1, 0.2), loc='lower left', ncol=num_cases)

    # Label groups
    #ax = plt.gca()
    #ax.set_xticklabels(timer_data.keys())
    #ax.set_xticks(xticks)
    plt.xlim(xticks[0]-1.0, xticks[-1]+1.0)
    plt.xticks([])

    # Run two-sample test and add table with speedup
    gnames = list(timer_data.keys())
    rows = ['Samples','Speedup', '99\% CI']
    sample_sizes = []
    speedup = []
    speedup_ci = []
    for gname, cases in timer_data.items():
        x, y = list(cases.values())
        logx, logy = np.log(x), np.log(y)

        # Trimmed sample sizes
        logx_trimmed = trim(logx)
        logy_trimmed = trim(logy)
        sample_sizes.append('%d, %d' % (len(logx_trimmed), len(logy_trimmed)))

        # Two-sample stats
        tstat, pval = trimmed_ttest(logx, logy, True)
        print(gname, list(cases.keys()))
        print('  tstat = %e, pval = %e\n' % (tstat, pval))

        # Speedup confidence interval
        logd_mean, logd_lower, logd_upper = trimmed_ttest_bounds(logx, logy)
        speedup.append('%1.2f' % np.exp(logd_mean))
        speedup_ci.append('(%1.2f, %1.2f)' % (np.exp(logd_lower), np.exp(logd_upper)))
    tbl = plt.table(cellText=[sample_sizes, speedup, speedup_ci], rowLabels=rows, colLabels=gnames, loc='bottom', cellLoc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(18)
    tbl.scale(1, 3.5)

    # Final plot
    plt.ylabel('Wall-clock time (s)')
    plt.tight_layout()
    ax = plt.gca()
    ax.set_axisbelow(True)
    ax.grid(linestyle='--', alpha=0.5)
    plt.show()


###################################################################################################
if __name__ == "__main__":
    '''
    Postprocessing for GIS1to10km MALI performance results
     - Extract timer data
     - Report on MALI performance improvements (memoization, semicoarsening, tuning)
    '''
    # Extract file names
    arch_ids = {'HSW':'hsw','KNL':'knl','PWR9':'pwr9','V100':'v100'}
    case_ids = {'Baseline':'1ws', 'Improvement':'mem'}
    file_data = {}
    for arch, arch_id in arch_ids.items():
        file_data[arch] = {}
        for case, case_id in case_ids.items():
            file_data[arch][case] = {}
            file_data[arch][case]['landice_files'] = glob.glob('TimerData/log.landice.timers.'+arch_id+ '.'+case_id+'.*.out')
            file_data[arch][case]['albany_files'] = glob.glob('TimerData/log.albany.timers.'+arch_id+ '.'+case_id+'.*.out')

    # Specify timers to extract from files (note: must be unique names in file)
    landice_timers = {'Total Time': '1 total time'}
    albany_timers = {'Total Fill': 'Albany: Total Fill Time:',
                     'Preconditioner Construction': 'NOX Total Preconditioner Construction:',
                     'Linear Solve': 'NOX Total Linear Solve:'}

    # Initialize iter and timer data
    for arch_data in file_data.values():
        for case_data in arch_data.values():
            case_data['nlin_iters'] = []
            case_data['linsol_time'] = []
            case_data['lin_iters'] = []
            case_data['prec_time'] = []
            case_data['timers'] = {}
            for timer in landice_timers.keys():
                case_data['timers'][timer] = []
            for timer in albany_timers.keys():
                case_data['timers'][timer] = []

    # Collect iter and timer data
    for arch_data in file_data.values():
        for case_data in arch_data.values():
            num_samples = len(case_data['albany_files'])
            for i in range(num_samples):
                # Extract iter data
                iter_data = MALIiters(case_data['albany_files'][i])
                case_data['nlin_iters'].append(iter_data['Nonlinear Iterations'])
                case_data['linsol_time'].append(iter_data['Total Linear Solve Time'])
                case_data['lin_iters'].append(iter_data['Linear Iterations'])
                case_data['prec_time'].append(iter_data['Total Preconditioner Apply Time'])

                # Extract timer data
                landice_info = {}
                landice_info['file'] = case_data['landice_files'][i]
                landice_info['timers'] = landice_timers
                albany_info = {}
                albany_info['file'] = case_data['albany_files'][i]
                albany_info['timers'] = albany_timers
                timers = MALItimers(landice_info, albany_info)
                for timer, wtime in timers.items():
                    case_data['timers'][timer].append(wtime)

    # Print solver data
    for arch, arch_data in file_data.items():
        for case, case_data in arch_data.items():
            # Check iterations
            #nliniters = np.mean(case_data['nlin_iters'])
            #liniters = np.mean(case_data['lin_iters'])
            #print(arch + ' ' + case + ': nliniter = %e, liniters = %e' % (nliniters, liniters))

            # Nonlinear iterations
            nliniters = int(np.mean(case_data['nlin_iters']))

            # Average linear iterations per linear solve
            avglinits = np.divide(case_data['lin_iters'], case_data['nlin_iters'])
            avg_li_mean, avg_li_lower, avg_li_upper = trimmed_bounds(avglinits)

            # Total Linear Solve Time
            logt = np.log(case_data['linsol_time'])
            logt_mean, logt_lower, logt_upper = trimmed_bounds(logt)
            t_mean, t_lower, t_upper = np.exp(logt_mean), np.exp(logt_lower), np.exp(logt_upper)

            # Print results
            print(arch + ' ' + case + ': nliniter = %d, avglinits = %1.1f (%1.1f, %1.1f), linsol = %1.1f (%1.1f, %1.1f)' % 
                    (nliniters, avg_li_mean, avg_li_lower, avg_li_upper, t_mean, t_lower, t_upper))

    # Dump timer data
    #print(json.dumps(file_data, sort_keys=False, indent=2))
    
    # Restructure case data based on timer data
    archs = tuple(arch_ids.keys())
    cases = tuple(case_ids.keys())
    timer_case_names = {'Total Time': {'Baseline':cases[0],'Improvement':cases[1]},
                        'Total Fill': {'Baseline':cases[0],'Improvement':cases[1]},
                        'Preconditioner Construction': {'Baseline':cases[0],'Improvement':cases[1]},
                        'Linear Solve': {'Baseline':cases[0],'Improvement':cases[1]}}
    timers_data = {}
    for timer, case_names in timer_case_names.items():
        timers_data[timer] = {}
        for arch in archs:
            timers_data[timer][arch] = {}
            for case_name, case in case_names.items():
                timers_data[timer][arch][case_name] = file_data[arch][case]['timers'][timer]

    # Colors for boxplots (two cases, three colors/case)
    bp_color_data = []
    bp_color_data.append({'boxfacecolor':(173/255, 221/255, 1),
                          'boxlinecolor':(66/255, 177/255, 1),
                          'errlinecolor':(0, 107/255, 182/255)})
    bp_color_data.append({'boxfacecolor':(206/255, 234/255, 230/255),
                          'boxlinecolor':(129/255, 201/255, 191/255),
                          'errlinecolor':(66/255, 154/255, 141/255)})
    #linecolor = (25/255,25/255,112/255)
    #facecolor = (135/255,206/255,235/255)
    colors_data = {}
    for timer, case_names in timer_case_names.items():
        colors_data[timer] = {}
        for i, case_name in enumerate(case_names.keys()):
            colors_data[timer][case_name] = bp_color_data[i]
    
    # Report performance improvements
    for timer, timer_data in timers_data.items():
        print(timer)
        color_data = colors_data[timer]
        ReportPerformanceImprovements(timer_data, color_data)

    # Report performance profiles
    total_time_data = timers_data.pop('Total Time')
    ReportPerformanceProfiles(timers_data, total_time_data)

