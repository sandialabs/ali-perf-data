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
def ReportPerformanceProfiles(timers_data, total_solve_data):
    '''
     - Compute mean proportions of 'Total Solve'
     - Construct a series of barplots to highlight bottlenecks
    '''
    # Get sizes for matrix
    num_timers = len(timers_data)
    num_cases = len(total_solve_data)
    num_archs = len(next(iter(total_solve_data.values())))

    # Compute mean proportions
    props = np.zeros((num_archs, num_cases, num_timers))
    for k, case_data in enumerate(timers_data.values()):
        for j, (arch_data, total_arch_data) in enumerate(zip(case_data.values(), total_solve_data.values())):
            for i, (wtimes, total_wtimes) in enumerate(zip(arch_data.values(), total_arch_data.values())):
                props[i,j,k] = np.sum(np.divide(np.array(wtimes), np.array(total_wtimes))) / len(wtimes)
    print("Proportions:")
    print(props)

    colors = (
        (0/255, 128/255, 128/255), # teal
        (128/255, 0/255, 128/255), # purple
        (255/255, 192/255, 203/255)) # pink
    textstr = r'''\underline{Resolution}
                 $a$: 16km
                 $b$: 8km
                 $c$: 4km
                 $d$: 2km
                 $e$: 1km'''

    # Plot results
    fig = plt.figure(figsize=(14,8))
    Groups = list(next(iter(total_solve_data.values())))
    Stacks = (('$a$','$b$','$c$','$d$','$e$'),('$a$','$b$','$c$','$d$','$e$'),('$a$','$b$','$c$','$d$','$e$'),('$a$','$b$','$c$','$d$','$e$'))
    Timers = list(timers_data.keys())
    h = plotBarStackGroups(props, Groups, Stacks, colors, False)
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
    tabYPos = 0.50
    plt.gcf().text(tabXPos, tabYPos, textstr,
            bbox=dict(boxstyle='round,pad=0.5',facecolor='none',edgecolor='black',linewidth=1.0,alpha=0.2))
    plt.subplots_adjust(right=0.68)
    plt.show()


###################################################################################################
def ReportPerformanceResults(timer_data, color_data):
    '''
     - Construct a series of boxplots to show performance results
    '''
    # Boxplots
    fig = plt.figure(figsize=(9,10))
    xticks = []
    for i, (gname, archs) in enumerate(timer_data.items()):
        xticks.append(i + 1)
        for j, (arch, wtimes) in enumerate(archs.items()):
            # Barplot
            pos = [i + 1,]
            bp = plt.boxplot(wtimes, positions=pos, widths=0.9, patch_artist=True, whis=[0,100], showcaps=False)
            
            # Change color
            boxlinecolor = color_data[arch]['boxlinecolor']
            bp['medians'][0].set(color=boxlinecolor, linewidth=2.0)
            bp['whiskers'][0].set(color=boxlinecolor, linewidth=2.0, linestyle='--')
            bp['whiskers'][1].set(color=boxlinecolor, linewidth=2.0, linestyle='--')
            bp['boxes'][0].set(color=boxlinecolor, linewidth=2.0)
            boxfacecolor = color_data[arch]['boxfacecolor']
            bp['boxes'][0].set_facecolor(boxfacecolor)

            # Mean errorbar for small sample size
            errlinecolor = color_data[arch]['errlinecolor']
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
    num_archs = len(color_data)
    archs = list(color_data.keys())
    legend_markers = []
    for arch, color in color_data.items():
        boxlinecolor = color['boxlinecolor']
        boxfacecolor = color['boxfacecolor']
        errlinecolor = color_data[arch]['errlinecolor']
        h = plt.errorbar(xticks[-1]+3.0, t_mean, yerr=[[1], [1]], fmt='s', color=errlinecolor, elinewidth=2, capsize=8, capthick=2, visible='off')
        legend_markers.append(h)
    plt.legend(legend_markers, archs, bbox_to_anchor=(0, 1.02, 1, 0.2), loc='lower left', ncol=num_archs)

    # Label groups
    #ax = plt.gca()
    #ax.set_xticklabels(timer_data.keys())
    #ax.set_xticks(xticks)
    plt.xlim(xticks[0]-(xticks[1]-xticks[0])/2.0, xticks[-1]+(xticks[-1]-xticks[-2])/2.0)
    plt.xticks([])

    # Run two-sample test and add table with speedup
    gnames = list(timer_data.keys())
    rows = ['Resolution','\# Nodes','Samples','Speedup', '99\% CI']
    res = ['16km','8km','4km','2km','1km']
    sample_sizes = []
    speedup = []
    speedup_ci = []
    for gname, archs in timer_data.items():
        twosamples = ('PWR9','V100')
        x = list(archs[twosamples[0]])
        y = list(archs[twosamples[1]])
        logx, logy = np.log(x), np.log(y)

        # Trimmed sample sizes
        logx_trimmed = trim(logx)
        logy_trimmed = trim(logy)
        sample_sizes.append('%d, %d' % (len(logx_trimmed), len(logy_trimmed)))

        ## Two-sample stats
        tstat, pval = trimmed_ttest(logx, logy, True)
        print(gname, twosamples)
        print('  tstat = %e, pval = %e' % (tstat, pval))

        # Speedup confidence interval
        logd_mean, logd_lower, logd_upper = trimmed_ttest_bounds(logx, logy)
        speedup.append('%1.2f' % np.exp(logd_mean))
        speedup_ci.append('(%1.2f, %1.2f)' % (np.exp(logd_lower), np.exp(logd_upper)))
    tbl = plt.table(cellText=[res, gnames, sample_sizes, speedup, speedup_ci], rowLabels=rows, loc='bottom', cellLoc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(18)
    tbl.scale(1, 3.5)

    # Report efficiencies
    node1 = timer_data['1']
    node1_dofs = 2203530
    node256 = timer_data['256']
    node256_dofs = 566117916
    nodes = 256
    for arch, x in node1.items():
        y = node256[arch]
        logx, logy = np.log(np.true_divide(x,node1_dofs)), np.log(np.true_divide(y,node256_dofs))

        # Trimmed sample sizes
        logx_trimmed = trim(logx)
        logy_trimmed = trim(logy)

        ## Two-sample stats
        tstat, pval = trimmed_ttest(logx, logy, True)
        print(arch + ' weak scaling efficiency:')
        print('  %d, %d' % (len(logx_trimmed), len(logy_trimmed)))
        print('  tstat = %e, pval = %e' % (tstat, pval))

        # Efficiency confidence interval
        logd_mean, logd_lower, logd_upper = trimmed_ttest_bounds(logx, logy)
        #print('  %1.1f%% (%1.1f, %1.1f)' % (100*np.exp(logd_mean)/nodes, 100*np.exp(logd_lower)/nodes, 100*np.exp(logd_upper)/nodes))
        print('  %1.2f%% (99%% CI: (%1.2f%%, %1.2f%%))' % (100*np.exp(logd_mean)/nodes, 100*np.exp(logd_lower)/nodes, 100*np.exp(logd_upper)/nodes))

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
    Postprocessing for AIS ALI weak scaling performance results
     - Extract timer data
     - Report on ALI weak scaling performance differences and efficiency
    '''
    # Extract file names
    cases_data = {}
    cases = ('ant16k20L.hsw','ant8k20L.hsw','ant4k20L.hsw','ant2k20L.hsw','ant1k20L.hsw',
             'ant16k20L.knl','ant8k20L.knl','ant4k20L.knl','ant2k20L.knl','ant1k20L.knl',
             'ant16k20L.pwr9','ant8k20L.pwr9','ant4k20L.pwr9','ant2k20L.pwr9','ant1k20L.pwr9',
             'ant16k20L.v100','ant8k20L.v100','ant4k20L.v100','ant2k20L.v100','ant1k20L.v100')
    for case in cases:
        cases_data[case] = {}
        cases_data[case]['timer_files'] = glob.glob('TimerData/out-'+case+'.*.txt')

    # Specify timers to extract from files (note: must be unique names in file)
    albany_timers = {}
    albany_timers['Total Time'] =                  'Albany Total Time:'
    albany_timers['Setup Time'] =                  'Albany: Setup Time:'
    albany_timers['Total Solve'] =                 'Piro::NOXSolver::evalModelImpl::solve:'
    albany_timers['Total Fill'] =                  'Albany: Total Fill Time:'
    albany_timers['Preconditioner Construction'] = 'NOX Total Preconditioner Construction:'
    albany_timers['Linear Solve'] =                'NOX Total Linear Solve:'

    # Initialize iter and timer data
    for case_data in cases_data.values():
        case_data['nlin_iters'] = []
        case_data['linsol_time'] = []
        case_data['lin_iters'] = []
        case_data['prec_time'] = []
        case_data['timers'] = {}
        for timer in albany_timers.keys():
            case_data['timers'][timer] = []

    # Collect iter and timer data
    for case, case_data in cases_data.items():
        for timer_file in case_data['timer_files']:
            # Extract iter data
            iter_data = MALIiters(timer_file)
            case_data['nlin_iters'].append(iter_data['Nonlinear Iterations'])
            case_data['linsol_time'].append(iter_data['Total Linear Solve Time'])
            case_data['lin_iters'].append(iter_data['Linear Iterations'])
            case_data['prec_time'].append(iter_data['Total Preconditioner Apply Time'])

            # Extract timer data
            data = {}
            data['file'] = timer_file
            data['timers'] = albany_timers
            timers = MALItimers(albany_info=data)
            for timer, wtime in timers.items():
                case_data['timers'][timer].append(wtime)
    
    # Print solver data
    for case, case_data in cases_data.items():
        # Check iterations
        #nliniters = np.mean(case_data['nlin_iters'])
        #liniters = np.mean(case_data['lin_iters'])
        #print(case + ': nliniter = %e, liniters = %e' % (nliniters, liniters))

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
        print(case + ': nliniter = %d, avglinits = %1.1f (%1.1f, %1.1f), linsol = %1.1f (%1.1f, %1.1f)' % 
                (nliniters, avg_li_mean, avg_li_lower, avg_li_upper, t_mean, t_lower, t_upper))

    # Dump timer data
    #print(json.dumps(cases_data, sort_keys=False, indent=2))
    
    # Colors for boxplots (four archs, three colors/arch)
    bp_color_data = []
    bp_color_data.append({'boxfacecolor':(192/255, 192/255, 1),
                          'boxlinecolor':(128/255, 128/255, 1),
                          'errlinecolor':(0, 0, 1)})
    bp_color_data.append({'boxfacecolor':(1, 192/255, 192/255),
                          'boxlinecolor':(1, 128/255, 128/255),
                          'errlinecolor':(1, 0, 0)})
    bp_color_data.append({'boxfacecolor':(192/255, 1, 192/255),
                          'boxlinecolor':(128/255, 1, 128/255),
                          'errlinecolor':(0, 1, 0)})
    bp_color_data.append({'boxfacecolor':(0, 1, 1),
                          'boxlinecolor':(0, 192/255, 192/255),
                          'errlinecolor':(0, 128/255, 128/255)})

    # Results
    timers = ('Total Solve', 'Total Fill', 'Preconditioner Construction', 'Linear Solve')
    group2res = {'1':'ant16k20L','4':'ant8k20L','16':'ant4k20L','64':'ant2k20L','256':'ant1k20L'}
    arch_ids = {'HSW':'hsw', 'KNL':'knl', 'PWR9':'pwr9', 'V100':'v100'}
    color_data = {}
    for i, arch in enumerate(arch_ids.keys()):
        color_data[arch] = {}
        bp_colors = bp_color_data[i]
        for bp_color_name, bp_color in bp_colors.items():
            color_data[arch][bp_color_name] = bp_color
    timers_data = {}
    for timer in timers:
        timers_data[timer] = {}
        timer_data = timers_data[timer]
        for group, res in group2res.items():
            timer_data[group] = {}
            for arch, arch_id in arch_ids.items():
                timer_data[group][arch] = cases_data[res+'.'+arch_id]['timers'][timer]
        print('\n'+timer)
        ReportPerformanceResults(timer_data, color_data)

    # Report performance profiles
    total_solve_data = timers_data.pop('Total Solve')
    ReportPerformanceProfiles(timers_data, total_solve_data)

