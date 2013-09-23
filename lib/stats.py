"""
Statistics.
"""


import numpy as np
from scipy.stats import gengamma, norm


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
    fname -- file name or object containing data columns to fit
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

    # remove 'unpack' and 'ndmin' kwargs if set
    for key in ['unpack','ndmin']:
        try:
            del kwargs[key]
        except KeyError:
            pass

    # read file
    cols = np.loadtxt(fname,unpack=True,ndmin=2,**kwargs)

    # set fitting distribution
    try:
        dist = eval(dist)
    except NameError:
        raise ValueError('invalid distribution: ' + dist)

    return (dist.fit(c) for c in cols)
