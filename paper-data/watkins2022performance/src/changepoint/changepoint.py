# Import libraries
import numpy as np
from scipy.stats import t as tdist

# Import functions
from trimmed_test import trimmed_ttest
from utils import make_numpy

###################################################################################################
def changepoint(x, alpha, num_tests=None):
    '''
    For each potential split point in a time series, perform a generalized
    likelihood test for a difference in the mean (equivalent to t-test for normal)
    Input:
        x         : time series input
        alpha     : significance level (e.g. 0.001). Since we perform multiple
                    hypothesis tests, we use the Bonferroni correction to avoid
                    inflated p-values (e.g. if testing 8 potential changepoints,
                    each changepoint is tested at the 0.001/8 significance level)
        num_tests : rank the first-order differences and only consider this many of
                    the largest differences (by absolute value). Making this smaller
                    saves time and increases the power of the test (assuming true
                    changepoint corresponds to a large change).
    Output:
        chgpts    : None if no significant changepoint detected, otherwise the index of
                    the detected changepoints (where i is a changepoint iff there was a
                    change between i-1 and i)
        stats     : t-stats associated with chgpts
    '''
    x = make_numpy(x)
    n = len(x)
    if n <= 2:
        return [], []
    if num_tests is None:
        num_tests = n-1
    
    # Performing (n-minRegime) t-tests; apply Bonferroni correction
    threshold = tdist.isf(alpha/(2*num_tests), df=n-2)

    # To save time, only check a few largest jumps in absolute value
    largest_jumps = 1 + np.argsort(
        [np.abs(x[i]-x[i-1]) for i in range(1, n)]
    )[-num_tests:]

    chgpts = []
    stats = []
    for k in largest_jumps:
        T = trimmed_ttest(x[:k], x[k:])
        if np.abs(T) >= threshold: 
            chgpts.append(k)
            stats.append(T)
    return chgpts, stats
        
###################################################################################################
class VoteHistory:
    '''
    Helper class for changepoint finder. Stores the candidate changepoints
    detected by several sources, and determines whether they agree on any.
    '''
    def __init__(self, num_votes):
        self.votes = [dict() for _ in range(num_votes)]
    def push(self, vote_dict):
        self.votes.append(vote_dict)
        self.votes.pop(0)
    def result(self):
        unanimous = set.intersection(*[set(d.keys()) for d in self.votes])
        if len(unanimous) == 0:
            return None
        else:
            options = [(k, sum(d[k] for d in self.votes)) for k in unanimous]
            best_option = max(options, key=lambda x: np.abs(x[1]))
            return best_option[0]
    def reset(self):
        self.votes = [dict() for _ in self.votes]
    
###################################################################################################
def seq_chgpts(x, alpha=0.0001, min_agree=3, num_tests=10, lookback=30, verbose=False):
    '''
    Apply changepoint detection method sequentially
    Input:
        x         : time series input
        alpha     : significance level to pass into the underlying model
        min_agree : minimum consecutive agreeing detections to determine a changepoint
        num_tests : only test this many of the largest changes - can save some time by
                    not considering every single data point as a potential changepoint
        lookback  : max number of data points to look backward in time (avoid hyper-
                    sensitivity as sample size grows)
        verbose   : print some output while using
    Output:
        chgpts    : list of detected changepoints (indices of x)
        detpts    : list of indices at which corresponding changepoints were detected
                    (a changepoint may not be detected until several observations after
                    the change)
    '''
    chgpts = [0]    # Identified changepoints
    detpts = [0]    # When each corresponding changepoint is detected
    votes = VoteHistory(min_agree)
    
    x = make_numpy(x)
    n = len(x)
    if n <= 2:
        return chgpts, detpts, votes
        
    i = 0           # Track starting point of current data under consideration
    j = i+1         # Consider data up to (but not including) index j
    while j <= n:
        # Find changepoints in x[i:j]
        vote_list, stats = changepoint(x[i:j], alpha, num_tests)
        new_votes = {vote+i: stat for vote, stat in zip(vote_list, stats)}
        if verbose:
            print('At idx %d, found candidates:' % (j-1), new_votes)
        votes.push(new_votes)
        chgpt = votes.result()
        if chgpt is not None:
            i = chgpt
            chgpts.append(chgpt)
            detpts.append(j-1)
            if verbose:
                print('At idx %d, found changepoint:' % (j-1), chgpt)
            
            # Now that we know i is a change point, go back to there
            j = chgpts[-1]+1
            votes.reset()
        else:
            j += 1
            i = max(i, j-lookback)
    return chgpts, detpts, votes

