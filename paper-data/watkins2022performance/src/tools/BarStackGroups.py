# Import libraries
import matplotlib.pyplot as plt
import numpy as np

def plotBarStackGroups(stackData, groupLabels, barLabels, colors, barLabelAbove = True):
    '''
    Plot stacked bars by group
    Input:
        stackData   : 3D numpy array with data organized as (groups, stacks, stack elements)
        groupLabels : list of group names
        barLabels   : list of bar names
        colors      : stack element colors
    '''
    h = []
    NumGroupsPerAxis, NumStacksPerGroup, NumElementsPerStack = stackData.shape
    #MaxGroupWidth = 0.65 # Fraction of 1. If 1, then we have all bars in groups touching
    MaxGroupWidth = 0.8
    groupOffset = MaxGroupWidth/NumStacksPerGroup
    #hatches = ['','/']

    if len(colors) is not NumElementsPerStack:
        raise RuntimeError('Size of colors does not match stack data.')

    for i in range(NumStacksPerGroup):
        # Center the bars:
        internalPosCount = i+1 - (NumStacksPerGroup+1) / 2

        # Offset the group draw positions:
        groupDrawPos = internalPosCount * groupOffset + np.arange(NumGroupsPerAxis)+1

        htemp = []
        htemp.append(plt.bar(groupDrawPos, stackData[:,i,0], groupOffset,
            color=colors[0], edgecolor=['k']*len(groupDrawPos))) # matplotlib bug
        #htemp.append(plt.bar(groupDrawPos, stackData[:,i,0], groupOffset, 
        #    color=colors[0], edgecolor=['k']*len(groupDrawPos), hatch=hatches[i])) # this one is for adding hatch
        #htemp.append(plt.bar(groupDrawPos, stackData[:,i,0], groupOffset, 
        #    color=colors[0], edgecolor='k'))
        top = stackData[:,i,0].copy()
        for j in range(1,NumElementsPerStack):
            htemp.append(plt.bar(groupDrawPos, stackData[:,i,j], groupOffset,
                bottom=top, color=colors[j], edgecolor=['k']*len(groupDrawPos))) # matplotlib bug
            #htemp.append(plt.bar(groupDrawPos, stackData[:,i,j], groupOffset, 
            #    bottom=stackData[:,i,j-1], color=colors[j], edgecolor='k'))
            top += stackData[:,i,j]
        h.append(htemp)

        # Bar Labeling (above)
        for j in range(NumGroupsPerAxis):
            if type(barLabels[0]) is list or type(barLabels[0]) is tuple:
                label = barLabels[j][i]
            else:
                label = barLabels[i]
            if (barLabelAbove):
                plt.text(groupDrawPos[j], top[j], label,
                    verticalalignment='bottom',horizontalalignment='center')
            else:
                plt.text(groupDrawPos[j], 0.98*top[j], label,
                    verticalalignment='top',horizontalalignment='center') # (below)

    plt.xticks(np.arange(NumGroupsPerAxis)+1, groupLabels)
    return h
