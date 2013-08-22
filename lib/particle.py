"""
A Particle contains information about a physical particle.
"""


from collections import namedtuple


__all__ = ['Particle', 'particle_filter']


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

or dictionaries, where fields are addressed by name but in a comparatively less
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

Particle = namedtuple('Particle', 'ID pT phi eta')



def particle_filter(particles,ID=[],charged=False,pTmin=None,pTmax=None,etamin=None,etamax=None):
    """
    Factory function:  creates a function to filter Particles with specified
    criteria.

    Usage
    -----
    >>> pf = particle_filter(criterion1,criterion2,...)

    Allowed criteria are:
    ID -- a list of particle IDs
    charged -- boolean, shortcut to select all charged particles
    pTmin,pTmax -- range of pT; can omit either min or max
    etamin,etamax -- range of eta; if only etamax, assume |eta| < etamax;
        if only etamin, assume etamin < |eta|

    After creating a particle_filter, it is applied to Particle objects.  All
    criteria must be met for the filter to return True, e.g.:

    >>> pf = particle_filter(ID=[211],pTmin=0.5,etamax=2.5)
    >>> p1 = Particle(ID=211,pT=1.0,phi=1.0,eta=1.0)
    >>> pf(p1)
    True
    >>> p2 = Particle(ID=211,pT=1.0,phi=1.0,eta=3.0)
    >>> pf(p2)
    False

    As its name suggests, a particle_filter() is ideal for use with Python's
    builtin filter(), e.g.:

    >>> list(filter(pf,(p1,p2)))
    [True, False]

    In general, iterables of particles may be filtered via

    >>> filter(particle_filter(...), particles)

    Note that particle_filter() returns True when applied to None.

    """

    # init. empty list of filters
    _filters = []

    ### create a lambda function for all specified criteria
    ### each lambda is a boolean function of Particle objects

    # match particle ID
    if ID:
        _filters.append(lambda Particle: abs(Particle.ID) in ID)

    # match charged particles
    if charged:
        # retrieve ID list from PDG class
        import pdg
        _charged = pdg.chargedIDs()
        _filters.append(lambda Particle: abs(Particle.ID) in _charged)


    # match pT range
    if pTmin and pTmax:
        _filters.append(lambda Particle: pTmin < Particle.pT < pTmax)

    elif pTmin and not pTmax:
        _filters.append(lambda Particle: pTmin < Particle.pT)

    elif pTmax and not pTmin:
        _filters.append(lambda Particle: Particle.pT < pTmax)


    # match eta range
    if etamax and etamin:
        _filters.append(lambda Particle: etamin < Particle.eta < etamax)

    elif etamin and not etamax:
        _filters.append(lambda Particle: etamin < abs(Particle.eta))

    elif etamax and not etamin:
        _filters.append(lambda Particle: abs(Particle.eta) < etamax)


    if _filters:
        # match all specified filters
        def func(Particle):
            return all(f(Particle) for f in _filters) if Particle else True
        return filter(func, particles)
    else:
        # if no filters, just return the iterable as is
        return particles
