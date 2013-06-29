"""
docstring
"""


import math


ZERO = 1e-16


class MissingValueError(Exception):
    pass


class Particle:
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
        return '{} {} {} {}'.format(self.ID, self.pT, self.phi, self.eta)


    def _calc_pT(self,px,py,sqrt=math.sqrt):
        return sqrt(px*px + py*py)

    def _calc_phi(self,px,py,atan2=math.atan2):
        return atan2(py,px)

    def _calc_eta(self,px,py,pz,sqrt=math.sqrt,log=math.log):
        pmag = sqrt(px*px + py*py + pz*pz)
        return 0.5*log((pmag+pz)/max(pmag-pz,ZERO))   # avoid division by zero
