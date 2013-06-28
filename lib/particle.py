"""
docstring
"""


from math import atan2, log, sqrt


class MissingValueError(Exception):
    pass


class Particle:
    def __init__(self,ID=None,px=None,py=None,pz=None,pT=None,phi=None,eta=None):
        if not ID:
            raise MissingValueError('Must provide a particle ID.')
        if not ( (px and py and pz) or (pT and phi and eta) ):
            raise MissingValueError('Must provide pT,phi,eta or px,py,pz.')

        self._ID = ID

        self._pT = pT or self._calc_pT(px=px,py=py)
        self._phi = phi or self._calc_phi(px=px,py=py)
        self._eta = eta or self._calc_eta(px=px,py=py,pz=pz)


    def __str__(self):
        return '{} {} {} {}'.format(self._ID, self._pT, self._phi, self._eta)


    def _calc_pT(self,px=None,py=None):
        return sqrt(px*px + py*py)

    def _calc_phi(self,px=None,py=None):
        return atan2(py,px)

    def _calc_eta(self,px=None,py=None,pz=None):
        pmag = sqrt(px*px + py*py + pz*pz)
        return 0.5*log((pmag+pz)/max(pmag-pz,1e-16))   # avoid division by zero


    def ID(self):
        return self._ID

    def pT(self):
        return self._pT

    def phi(self):
        return self._phi

    def eta(self):
        return self._eta


    def standard_info(self):
        #return dict(ID=self._ID, pT=self._pT, phi=self._phi, eta=self._eta)
        return self._ID, self._pT, self._phi, self._eta
