"""
A Particle contains information about physical particles.
"""


import math


# small quantity > 0
# used to avoid division by zero
ZERO = 1e-16


class MissingValueError(Exception):
    """ Trivial Exception subclass.  For display purposes. """
    pass


class Particle:
    """
    The base implementation of the module.  It stores standard particle
    information.


    Instantiation
    -------------
    >>> Particle(ID=ID,px=px,py=py,pz=pz)
    >>> Particle(ID=ID,pT=pT,phi=phi,eta=eta)

    In the former case, pT,phi,eta are calculated from px,py,pz via the methods
    _calc_<var>.  In both cases, pT,phi,eta become attributes of the instance.


    Notes
    -----
    The __str__ method has been manually defined to return standard particle
    information.  This is very convenient for printing to stdout, e.g.

    >>> p = Particle(ID=211,pT=0.5,phi=1.0,eta=2.0)
    >>> print(p)
    211 0.5 1.0 2.0

    """

    def __init__(self,ID=None,px=None,py=None,pz=None,pT=None,phi=None,eta=None):
        if not ID:
            raise MissingValueError('Must provide a particle ID.')
        if not ( (px and py and pz) or (pT and phi and eta) ):
            raise MissingValueError('Must provide pT,phi,eta or px,py,pz.')

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
        return 0.5*log((pmag+pz)/max(pmag-pz,ZERO))   # avoid division by zero
