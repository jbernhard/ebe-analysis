"""
Statistics.
"""


import numpy as np
from scipy.stats import gengamma


"""
Set default starting parameters for fitting a generalized gamma distribution.

These parameters are sensible for ATLAS v_n distributions.

Order:  (a, c, loc, scale)  where a,c are shape params.
"""
gengamma._fitstart = lambda data: (1.0, 2.0, 0.0, 0.1)


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
