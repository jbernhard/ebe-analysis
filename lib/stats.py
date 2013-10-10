"""
Statistics.
"""


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
