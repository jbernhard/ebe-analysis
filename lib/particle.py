"""
A Particle contains information about a physical particle.
"""


__all__ = ['Particle', 'particle_filter']



class Particle:
    """
    Stores standard particle information (ID,pT,phi,eta).

    Usage
    -----
    A Particle is typically created with positional arguments

    >>> Particle(ID,pT,phi,eta)

    Keyword arguments also work

    >>> Particle(pT=1.0,phi=2.0,eta=3.0,ID=211)

    Standard order (ID,pT,phi,eta) is retained even if the Particle is created with
    out-of-order keyword arguments.

    Fields are addressed directly by name

    >>> p = Particle(211,1.0,2.0,3.0)
    >>> p.pT
    1.0

    This is superior to a list/tuple, where fields must be addressed by index

    >>> p[1]

    or dictionaries, where fields are addressed by name but in a comparatively less
    readable manner

    >>> p['pT']

    The string representation of a Particle is a space-separated list
    of its properties:

    >>> print(p)
    211 1.0 2.0 3.0

    """

    __slots__ = ('ID','pT','phi','eta')

    def __init__(self,ID=0,pT=0.0,phi=0.0,eta=0.0):
        self.ID = ID
        self.pT = pT
        self.phi = phi
        self.eta = eta

    def __str__(self):
        # fastest way to create the string
        # faster than ' '.join(...)
        # also, print(p) with __str__ is faster than print(*p) with __iter__

        return '{} {} {} {}'.format(self.ID,self.pT,self.phi,self.eta)

    def __repr__(self):
        return 'Particle(ID={}, pT={}, phi={}, eta={})'.format(self.ID,self.pT,self.phi,self.eta)




def particle_filter(particles,**kwargs):
    """
    Filter an iterable of particles according to specified critera.

    Typical usage is

    >>> particles = particle_filter(particles, **filterargs)

    Arguments
    ---------
    particles -- iterable of Particle objects
    kwargs -- filtering criteria

    Allowed criteria are:
    ID -- a list of particle IDs
    charged -- boolean, shortcut to select all charged particles
    pTmin,pTmax -- range of pT; ok to specify only one
    etamin,etamax -- range of eta
        if only etamax, interpreted as |eta| < etamax
        if only etamin, interpreted as etamin < |eta|

    Returns
    -------
    filtered iterable of particles
    if no filtering criteria were specified, returns particles unmodified

    Notes
    -----
    The filter evaluates to True on None.  This ensures proper event separation
    with particles_from_<format> generators.

    """

    # init. empty list of filters
    _filters = []

    ### create a lambda function for all specified criteria
    ### each lambda is a boolean function of Particle objects

    ID = kwargs.get('ID',[])
    charged = kwargs.get('charged',False)

    assert not (ID and charged)

    # match particle ID
    if ID:
        _filters.append(lambda p: p.ID in ID)

    # match charged particles
    if charged:
        # retrieve ID list from PDG class
        from . import pdg
        _charged = pdg.chargedIDs()
        _filters.append(lambda p: abs(p.ID) in _charged)


    pTmin = kwargs.get('pTmin',None)
    pTmax = kwargs.get('pTmax',None)

    # match pT range
    if pTmin and pTmax:
        assert 0 < pTmin < pTmax
        _filters.append(lambda p: pTmin < p.pT < pTmax)

    elif pTmin and not pTmax:
        assert pTmin > 0
        _filters.append(lambda p: pTmin < p.pT)

    elif pTmax and not pTmin:
        assert pTmax > 0
        _filters.append(lambda p: p.pT < pTmax)


    etamin = kwargs.get('etamin',None)
    etamax = kwargs.get('etamax',None)

    # match eta range
    if etamax and etamin:
        assert etamin < etamax
        _filters.append(lambda p: etamin < p.eta < etamax)

    elif etamin and not etamax:
        assert etamin > 0
        _filters.append(lambda p: etamin < abs(p.eta))

    elif etamax and not etamin:
        assert etamax > 0
        _filters.append(lambda p: abs(p.eta) < etamax)


    if _filters:
        # create a filtered iterable
        # True if all specified criteria are satisfied
        # or if the "particle" is None
        return (p for p in particles if p is None or all(f(p) for f in _filters))
    else:
        # if no filters, just return the iterable as is
        return particles
