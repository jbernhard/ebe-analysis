"""
A Particle contains information about a physical particle.
"""


import math
from .pdg import PDG


class Particle:
    """
    Stores standard particle information.

    Usage
    -----
    >>> Particle(ID=ID,px=px,py=py,pz=pz)
    >>> Particle(ID=ID,pT=pT,phi=phi,eta=eta)

    In the former case, pT,phi,eta are calculated from px,py,pz via the methods
    _calc_<var>.  In both cases, pT,phi,eta become attributes of the instance.

    The __str__ method has been manually defined to return standard particle
    information.  This is very convenient for printing to stdout, e.g.

    >>> p = Particle(ID=211,pT=0.5,phi=1.0,eta=2.0)
    >>> print(p)
    211 0.5 1.0 2.0

    """

    def __init__(self,ID=None,px=None,py=None,pz=None,pT=None,phi=None,eta=None):
        self.ID = ID

        self.pT = pT or self._calc_pT(px,py)
        self.phi = phi or self._calc_phi(px,py)
        self.eta = eta or self._calc_eta(px,py,pz)

    def __str__(self):
        # fastest way I have found to create the string
        # _much_ faster than ' '.join(str(i) for i in (...))
        # also faster than returning a tuple and print(*tuple)
        return '{} {} {} {}'.format(self.ID, self.pT, self.phi, self.eta)


    def _calc_pT(self,px,py,sqrt=math.sqrt):
        return sqrt(px*px + py*py)

    def _calc_phi(self,px,py,atan2=math.atan2):
        return atan2(py,px)

    def _calc_eta(self,px,py,pz,sqrt=math.sqrt,log=math.log):
        pmag = sqrt(px*px + py*py + pz*pz)
        return 0.5*log((pmag+pz)/max(pmag-pz,1e-10))   # avoid division by zero



class ParticleFilter:
    """
    Creates a function to filter Particles with specified criteria.  The
    function returns True if all criteria are met, else False.

    Usage
    -----
    >>> pf = ParticleFilter(criterion1,criterion2,...)

    Allowed criteria are:
    ID -- a list of particle IDs
    charged -- boolean, shortcut to select all charged particles
    pTmin,pTmax -- range of pT; can omit either min or max
    etamin,etamax -- range of eta; if only etamax, assume |eta| < etamax;
        if only etamin, assume etamin < |eta|

    After creating a ParticleFilter, it is then applied to Particle objects,
    e.g.

    >>> pf = ParticleFilter(IDlist=[211],pTmin=0.5,etamax=2.5)
    >>> p1 = Particle(ID=211,pT=1.0,phi=1.0,eta=1.0)
    >>> pf(p1)
    True
    >>> p2 = Particle(ID=211,pT=1.0,phi=1.0,eta=3.0)
    >>> pf(p2)
    False

    """

    def __init__(self,ID=[],charged=False,pTmin=None,pTmax=None,etamin=None,etamax=None):
        # init. empty list of filters
        self._filters = []

        ### create a lambda function for all specified criteria
        ### each lambda is a boolean function of Particle objects

        # match particle ID
        if ID:
            self._filters.append(lambda Particle: abs(Particle.ID) in ID)

        # match charged particles
        if charged:
            # retrieve ID list from PDG class
            pdg = PDG()
            self._charged = pdg.charged()
            del pdg
            self._filters.append(lambda Particle: abs(Particle.ID) in self._charged)


        # match pT range
        if pTmin and pTmax:
            self._filters.append(lambda Particle: pTmin < Particle.pT < pTmax)

        elif pTmin and not pTmax:
            self._filters.append(lambda Particle: pTmin < Particle.pT)

        elif pTmax and not pTmin:
            self._filters.append(lambda Particle: Particle.pT < pTmax)


        # match eta range
        if etamax and etamin:
            self._filters.append(lambda Particle: etamin < Particle.eta < etamax)

        elif etamin and not etamax:
            self._filters.append(lambda Particle: etamin < abs(Particle.eta))

        elif etamax and not etamin:
            self._filters.append(lambda Particle: abs(Particle.eta) < etamax)


    def __call__(self,Particle):
        # match all filter functions
        return all(f(Particle) for f in self._filters)
