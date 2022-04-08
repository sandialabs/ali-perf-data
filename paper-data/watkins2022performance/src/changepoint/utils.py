# Import libraries
import numpy as np

def make_numpy(*args):
    if len(args) == 1:
        return np.asarray(args[0])
    else:
        return tuple(np.asarray(x) for x in args)

