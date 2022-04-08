# Import libraries
import numpy as np
from scipy.stats import t as tdist, median_absolute_deviation as mad

# Import functions
from utils import make_numpy

###################################################################################################
def trim(x, p=.1, threshold=3, outliers=False):
    '''
    Remove observations that may be outliers - suspiciously far from the average.
    At most [floor(len(x)*p)] points are removed.
    Input:
        x : data to trim
        p : proportion of data to remove
    '''
    n = len(x)
    if p == 0 or n < np.ceil(1/p):
        return (x, []) if outliers else x

    # Trim most extreme observations if more than [threshold] std away.
    n_remove = int(np.floor(n*p))
    dev = np.abs(x - np.median(x))/(mad(x) + 1e-8)
    order = np.argsort(np.abs(x - np.median(x)))

    keep = []
    out = []
    for i in range(n):
        if dev[i] < threshold or i in order[:n-n_remove]:
            keep.append(i)
        else:
            out.append(i)

    return (x[keep], x[out]) if outliers else x[keep]

###################################################################################################
def trim_mean(x, p=.1):
    '''
    Trim a series to remove egregious outliers, and then return the mean.
    Input:
        x : series to trim
        p : maximum proportion of data to remove
    '''
    return trim(x, p).mean()

###################################################################################################
def trim_std(x, p=.1):
    '''
    Trim a series to remove egregious outliers, and then return the standard deviation.
    Inputs:
        x : series to trim
        p : maximum proportion of data to remove
    '''
    return trim(x, p).std()

###################################################################################################
def trimmed_stats(x, p=.1, var=True):
    '''
    Get trimmed mean and std or variance
    '''
    if var:
        return trim_mean(x, p), np.square(trim_std(x, p))
    else:
        return trim_mean(x, p), trim_std(x, p)

###################################################################################################
def trimmed_ttest(x, y=None, with_pval=False):
    '''
    Get t-statistic for difference in two independent samples with unequal variance.
    Useful if the means of the samples are roughly normal (e.g. data is normal, or
    sample size large enough, say 30+)
    Input:
        x, y : samples to compare. If y is None, performs one-sample t-test of mean==0
    '''
    x = make_numpy(x)
    xmean, xvar = trimmed_stats(x, var=True)
    if y is None:
        n = len(x)
        tstat = xmean / (np.sqrt(xvar/(n-2)) + 1e-8)
    else:
        y = make_numpy(y)
        ymean, yvar = trimmed_stats(y, var=True)
        k, n = len(x), len(x)+len(y)
        if n <= 2:
            return (0, 1) if with_pval else 0

        rss = (k-1)*xvar + (n-k-1)*yvar
        sigma = np.sqrt(rss/(n-2)) + 1e-8
        tstat = np.sqrt(k*(n-k)/n)*(ymean-xmean)/sigma
    pval = 2*tdist.cdf(-np.abs(tstat), n-2)
    return (tstat, pval) if with_pval else tstat

###################################################################################################
def trimmed_ttest_bounds(x, y, p=.1, alpha=0.01, num_tests=1):
    '''
    Get confidence interval for the difference between means
    '''
    x = make_numpy(x)
    xmean, xvar = trimmed_stats(x, p, var=True)
    n = len(x)
    y = make_numpy(y)
    ymean, yvar = trimmed_stats(y, p, var=True)
    m = len(y)

    rss = (n-1)*xvar + (m-1)*yvar
    sigma = np.sqrt(rss/(n+m-2)) + 1e-8
    stderr = sigma / np.sqrt(n*m/(n+m))
    #tstat = np.sqrt(n*m/(n+m))*(ymean-xmean)/sigma
    tcrit = tdist.isf(alpha/(2*num_tests), df=n+m-2)
    meandiff = xmean-ymean
    upper = meandiff + tcrit * stderr
    lower = meandiff - tcrit * stderr
    return meandiff, lower, upper

###################################################################################################
def trimmed_bounds(x, p=.1, alpha=0.01):
    '''
    Get confidence interval for the mean of a trimmed time series
    '''
    x = make_numpy(x)
    n = len(x)
    mean, std = trimmed_stats(x, p, var=False)
    stderr = std / np.sqrt(n)
    tcrit = tdist.isf(alpha/2, n-1)
    upper = mean + tcrit * stderr
    lower = mean - tcrit * stderr
    return mean, lower, upper

