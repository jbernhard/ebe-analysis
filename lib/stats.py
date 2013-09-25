"""
Statistics.
"""


from itertools import starmap

import numpy as np
import matplotlib.pyplot as plt
from numpy.random import uniform
from scipy.stats import gengamma
from scipy.optimize import curve_fit


def gengamma_start(data=None):
    """
    Generate random starting parameters for fitting a generalized gamma
    distribution.  Randomization is necessary to avoid systematic convergence
    problems.

    Parameter ranges are sensible for v_n distributions.

    Returns
    -------
    (a, c, loc, scale) -- where a,c are shape params.

    """

    return tuple(starmap(uniform, ((0.1,2.0),(1.0,5.0),(-0.1,0.1),(0.01,0.3))))

gengamma._fitstart = gengamma_start


def fit_file(fname,dist='gengamma',**kwargs):
    """
    Fit a distribution to each column of a data file.

    Arguments
    ---------
    fname -- file object, filename, or generator containing data columns to fit
    dist -- distribution to fit, either 'gengamma' (default) or 'norm'
    kwargs -- for np.loadtxt, except 'unpack' or 'ndmin' are ignored

    Returns
    -------
    iterable of MLE parameters:

        params_0, ... , params_N

    for each column, where params are tuples of the form

        (*shapes, loc, scale)

    as produced by scipy.stats.rv_continuous.fit

    """

    # ignore divide by zero errors
    # happens when the pdf vanishes because log pdf is used for optimization
    # doesn't affect the final result
    np.seterr(divide='ignore')

    # remove 'unpack' and 'ndmin' kwargs if set
    for key in ['unpack','ndmin']:
        try:
            del kwargs[key]
        except KeyError:
            pass

    # read file
    cols = np.loadtxt(fname,unpack=True,ndmin=2,**kwargs)

    # set fitting distribution
    if dist == 'norm':
        # fitting a gaussian is equivalent to calculating mean and stddev.
        # but the latter is much faster
        _fit = describe

    else:
        try:
            dist = eval(dist)
        except NameError:
            raise ValueError('invalid distribution: ' + dist)
        else:
            _fit = dist.fit

    return map(_fit, cols)


def describe(data):
    """
    Calculate descriptive stats (mean, stddev).

    Arguments
    ---------
    data -- array-like

    Returns
    -------
    (mean, stddev)

    """

    data = np.asarray(data)

    return (data.mean(), data.std())
