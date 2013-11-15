"""
Statistics.
"""


from functools import partial
import math

import numpy as np
import matplotlib.pyplot as plt
import scipy.special as spsp
import scipy.stats as spst
import scipy.optimize as spop



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
    """ Convert a string to a scipy.stats distribution object. """

    try:
        dist = getattr(spst,dist)
    except AttributeError:
        raise ValueError('invalid distribution: ' + dist)

    return dist


"""
Starting parameters for fitting the generalized gamma distribution.

Flow distributions seem to consistently have rms ~ scale.

order:  a, c, loc, scale -- where a,c are shape params.

"""

spst.gengamma._fitstart = lambda *args: (1., 2., 0., rms(*args))

# fix loc = 0 when fitting gengamma
spst.gengamma.fit = partial(spst.gengamma.fit, floc=0)


class rice_gen(spst.rv_continuous):
    """
    The Rice / Bessel-Gaussian distribution with standard parameterization.
    Overrides scipy.stats.rice.

    Parameters are named for flow distributions:

        vrp -- v_n reaction-plane
        dv -- delta v_n

    The PDF is

        f(v;vrp,dv) = v/dv^2 * exp(-(v^2+vrp^2)/(2*dv^2)) * I[0](v*vrp/dv^2)

    for v, vrp, dv > 0.

    The scipy location and scale parameters should be left fixed at defaults.
    The fit method is set to do this automatically and only returns vrp,dv.
    This is a bit of a hack but should be transparent to the user.

    """

    def _pdf(self, v, vrp, dv, exp=np.exp, i0=spsp.i0):
        dv2 = dv*dv
        return v / dv2 * exp(-0.5*(v*v+vrp*vrp)/dv2) * i0(v*vrp/dv2)

    def _logpdf(self, v, vrp, dv, log=np.log, i0=spsp.i0):
        dv2 = dv*dv
        return log(v/dv2) - 0.5*(v*v + vrp*vrp)/dv2 + log(i0(v*vrp/dv2))

    def _argcheck(self,*args):
        vrp,dv = args
        return (vrp >= 0) & (dv > 0)

    def _fitstart(self,data):
        """ Rough starting fit parameters, based on ATLAS results. """

        mean = data.mean()
        std = data.std()
        return np.sqrt(mean**2-std**2), std, 0, 1

    def fit(self, data, *args, **kwargs):
        """ Fit with fixed location and scale. """

        return super().fit(data,floc=0,fscale=1)[:2]

spst.rice = rice_gen(a=0.0, name="rice", shapes="vrp,dv")


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

    def __init__(self,data,dist='rice',maxstd=10):
        self.dist = validate_dist(dist)

        # flatten
        data = np.ravel(data)

        # remove outliers and store
        self.data = data[np.abs(data - data.mean()) < maxstd*data.std()]


    @classmethod
    def from_table(cls,data,dist='rice',**kwargs):
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


    def ks(self,*args,**kwargs):
        """
        Perform the Kolmogorov-Smirnov test for goodness of fit.

        Arguments
        ---------
        *args -- dist. parameters to test against
        **kwargs -- for scipy.stats.kstest

        Returns
        -------
        D,p -- KS test statistic, corresponding p-value

        """

        return spst.kstest(self.data,self.dist.name,args=args,**kwargs)


    def fit(self):
        """
        Calculate MLE distribution parameters.

        Returns
        -------
        *shapes, loc, scale -- as produced by scipy.stats.rv_continuous.fit

        """

        if self.dist is spst.norm:
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

        if self.dist is spst.norm:
            return self.describe()

        if self.dist is spst.gengamma:
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

        popt, pcov = spop.curve_fit(f, self.x, self.y, p0=p0, sigma=sigma)
        popt = popt.tolist()

        if self.dist is spst.gengamma:
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



def unfold(dv=None,M=None):
    """
    Unfold flow distributions by reducing width according to multiplicity.

    Arguments
    ---------
    dv -- array-like of Rice distribution widths
    M -- array-like of multiplicities

    Returns
    -------
    unfolded dv

    """

    dv = np.asarray(dv)
    M = np.asarray(M)

    return np.sqrt(np.maximum(dv*dv - 0.5/M,1e-8))
