"""
A Particle contains information about a physical particle.
"""


import collections
import math

from .pdg import PDG



"""
The Particle class.

Stores standard particle information (ID,pT,phi,eta) using the
collections.namedtuple container.

Usage
-----
A Particle is typically created with positional arguments

>>> Particle(ID,pT,phi,eta)

Keyword arguments also work

>>> Particle(211,1.0,2.0,3.0) == Particle(pT=1.0,phi=2.0,eta=3.0,ID=211)
True

Fields are addressed directly by name

>>> p = Particle(211,1.0,2.0,3.0)
>>> p.pT
1.0

This is superior to a regular tuple, where fields must be addressed by index

>>> p[1]

or dictionaries, where fields are addressed by name but in a comparitively less
readable manner

>>> p['pT']

The namedtuple retains order, unlike a dictionary

>>> list(p)
[211, 1.0, 2.0, 3.0]
>>> print(*p)
211 1.0 2.0 3.0

Standard order (ID,pT,phi,eta) is retained even if the Particle is created with
out-of-order keyword arguments.

"""

Particle = collections.namedtuple('Particle', 'ID pT phi eta')



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
