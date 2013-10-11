"""
Statistics.
"""


from functools import partial

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gengamma, norm
from scipy.optimize import curve_fit



"""
Plot style settings.

"""

_figwidth = 10

plt.rc('figure', figsize=[_figwidth,_figwidth/1.618], facecolor='1.0')
plt.rc('font', family='serif')
plt.rc('axes', color_cycle=['#33b5e5','#99cc00','#ff4444','#aa66cc','#ffbb33'])
plt.rc('lines', linewidth=1.5)
plt.rc('patch', linewidth=1.5)



def rms(x,y=None):
    """
    Calculate the root mean square of a data set.

    Arguments
    ---------
    x -- array-like, required
    y -- array-like, optional

    If y is ommitted, the RMS of x is calculated.  If both x and y are
    specified, x is interpreted as bin locations and y as the corresponding bin
    values.

    Returns
    -------
    rms -- float

    """

    x = np.asarray(x)

    if y is None:
        return np.sqrt(np.mean(np.square(x)))
    else:
        y = np.asarray(y)
        return np.sqrt( np.sum(y*np.square(x)) / np.sum(y) )


def validate_dist(dist):
    """ Convert a string to a scipy distribution object. """

    try:
        dist = eval(dist)
    except NameError:
        raise ValueError('invalid distribution: ' + dist)

    return dist


"""
Starting parameters for fitting the generalized gamma distribution.

Flow distributions seem to consistently have rms ~ scale.

order:  a, c, loc, scale -- where a,c are shape params.

"""

gengamma._fitstart = lambda *args: (1., 2., 0., rms(*args))

# fix loc = 0 when fitting gengamma
gengamma.fit = partial(gengamma.fit, floc=0)

class RawData:
    """
    Store raw (unbinned) data and provide related methods.

    Arguments
    ---------
    data -- array-like, will be flattened
    dist -- name of scipy distribution which is expected to describe the data
    maxstd -- maximum allowed standard deviations from the mean;
              points further away are removed

    """

    def __init__(self,data,dist='gengamma',maxstd=10):
        self.dist = validate_dist(dist)

        # flatten
        data = np.ravel(data)

        # remove outliers and store
        self.data = data[np.abs(data - data.mean()) < maxstd*data.std()]


    @classmethod
    def from_table(cls,data,dist='gengamma',**kwargs):
        """
        Create several RawData instances from the columns of tabular data.  Each
        column is expected to correspond to a separate data set.

        Arguments
        ---------
        data -- array-like, file object, filename, or generator containing
                tabular data
        dist -- same as for __init__
        kwargs -- passed to np.loadtxt if reading a file

        Returns
        -------
        iterable of RawData instances for each column

        """

        if any(isinstance(data,t) for t in (np.ndarray,list,tuple)):
            data = np.asarray(data).T
        else:
            kwargs.update(unpack=True)
            data = np.loadtxt(data,**kwargs)

        data = np.atleast_2d(data)

        return (cls(col,dist=dist) for col in data)


    def describe(self):
        """ Calculate mean and standard deviation. """

        return self.data.mean(), self.data.std()


    def fit(self):
        """
        Calculate MLE distribution parameters.

        Returns
        -------
        *shapes, loc, scale -- as produced by scipy.stats.rv_continuous.fit

        """

        if self.dist is norm:
            return self.describe()
        else:
            return self.dist.fit(self.data)


    def plot(self):
        """ Fit and plot the data. """

        x = np.linspace(self.data.min(),self.data.max(),100)

        params = self.fit()

        plt.plot(x, self.dist.pdf(x, *params))
        plt.hist(self.data, bins=int(2*self.data.size**.33),
                histtype='step', normed=True)

        plt.show()


class BinnedData:
    """
    Store unbinned data and provide related methods.

    Arguments
    ---------
    data -- array-like with 2-5 columns, see below
    dist -- name of scipy distribution which is expected to describe the data

    The first two columns should contain x and y values; the remaining column[s]
    should contain errors:

    1 error column  -- symmetrical errors
    2 error columns -- high and low errors
    3 error columns -- stat, syshigh, syslow errors [to be added in quadrature]

    """

    def __init__(self,data,dist='gengamma'):
        self.dist = validate_dist(dist)

        data = np.asarray(data).T

        try:
            self.x = data[0]
            self.y = data[1]
        except IndexError:
            raise ValueError('data must have 2-5 columns')

        ncol = data.shape[0]

        if ncol == 2:
            self.errhigh = self.errlow = None

        elif ncol == 3:
            self.errhigh = self.errlow = data[2]

        elif ncol == 4:
            self.errhigh, self.errlow = data[2:]

        elif ncol == 5:
            stat, *sys = data[2:]
            self.errhigh, self.errlow = (np.sqrt(stat*stat + s*s) for s in sys)

        else:
            raise ValueError('data must have 2-5 columns')


    @classmethod
    def from_file(cls,data,dist='gengamma',**kwargs):
        """
        Create an instance from a tabular data file.  Columns follow the same
        format as in __init__.

        Arguments
        ---------
        data -- file object, filename, or generator containing tabular data
        dist -- same as for __init__
        kwargs -- passed to np.loadtxt

        """

        kwargs.update(unpack=False)
        data = np.loadtxt(data,**kwargs)

        return cls(data,dist=dist)


    def describe(self):
        """ Calculate mean and standard deviation. """

        w = np.sum(self.y)

        mu = np.sum(self.x*self.y) / w
        sigma = np.sqrt( np.sum( np.square(self.x - mu) * self.y) / w )

        return mu, sigma


    def fit(self):
        """
        Calculate least-squares distribution parameters.

        Returns
        -------
        *shapes, loc, scale -- as produced by scipy.optimize.curve_fit

        """

        if self.dist is norm:
            return self.describe()

        if self.dist is gengamma:
            # fix location parameter to zero
            def f(x,*p):
                return self.dist.pdf(x,p[0],p[1],0,p[-1])

            p0 = self.dist._fitstart(self.x,self.y)
            p0 = p0[:2] + p0[3:]
        else:
            f = self.dist.pdf
            p0 = None

        try:
            sigma = np.maximum(self.errhigh,self.errlow)
        except TypeError:
            sigma = None

        popt, pcov = curve_fit(f, self.x, self.y, p0=p0, sigma=sigma)
        popt = popt.tolist()

        if self.dist is gengamma:
            popt.insert(2,0)

        return tuple(popt)


    def plot(self):
        """ Fit and plot the data. """

        X = np.linspace(0,self.x.max(),100)

        params = self.fit()

        yerr = self.errlow if self.errlow is self.errhigh \
                else (self.errlow, self.errhigh)

        plt.errorbar(self.x, self.y, yerr=yerr, fmt='o')
        plt.plot(X, self.dist.pdf(X, *params))

        plt.show()
