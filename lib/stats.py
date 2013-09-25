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



class ATLASData:
    """
    Read, store, and provide methods for ATLAS flow data.

    Usage
    -----
    >>> ATLASData(fname)

    where fname is a file containing columns v_n, p(v_n), stat, syshigh, syslow.

    The primary public methods are fit() and plot().

    """

    def __init__(self,fname):
        # read and store data
        for attr,col in zip(
                ('v','pv','stat','syshigh','syslow'),
                np.loadtxt(fname,unpack=True)):
            setattr(self, attr, col)

        self._fit = None


    @staticmethod
    def add_quadrature(v1,v2):
        """ Add two errors in quadrature. """
        return np.sqrt(v1*v1 + v2*v2)

    def errhigh(self):
        """ High stat+sys error. """
        return self.add_quadrature(self.stat, self.syshigh)

    def errlow(self):
        """ Low stat+sys error. """
        return self.add_quadrature(self.stat, self.syslow)

    def errmax(self):
        """ stat+sys error, max of high and low. """
        return np.maximum(self.errhigh(), self.errlow())


    def fit(self,retry=10,errtol=10.0):
        """
        Fit data to a generalized gamma distribution.

        Optional arguments
        ------------------
        retry -- maximum number of times to retry the fit
        errtol -- maximum error tolerance

        Returns
        -------
        popt, pcov, perr

        popt -- optimal parameters from scipy.optimize.curve_fit
        pcov -- covariance of popt from scipy.optimize.curve_fit
        perr -- total squared error with popt

        """

        # don't redo the fit
        if self._fit is None:
            # retry the fit until the error tolerance is satisfied
            for i in range(retry):
                try:
                    # scipy least squares fit
                    popt, pcov = curve_fit(gengamma.pdf, self.v, self.pv,
                            p0=gengamma_start(), sigma=self.errmax())

                except RuntimeError:
                    # retry on error
                    continue

                else:
                    # total squared error
                    perr = np.sum(np.square(
                        (gengamma.pdf(self.v, *popt) - self.pv)/self.errmax()
                        ))

                    # retry if error is too large
                    if perr < errtol:
                        self._fit = (popt,pcov,perr)
                        break

            else:
                # the fit failed for all retries
                raise RuntimeError('fit did not succeed after ' + str(retry) +
                ' iterations')

        return self._fit


    def plot(self):
        """ Fit and plot the data. """

        x = np.linspace(0,self.v.max(),100)

        params, *rest = self.fit()

        plt.semilogy(x, gengamma.pdf(x, *params))
        plt.errorbar(self.v, self.pv,
                yerr=(self.errlow(), self.errhigh()),
                fmt='go')
        plt.show()
