"""
An Event is a collection of Particles.
"""


import numpy as np


class Event:
    """
    The base implementation of the module.  It stores a list of Particles and
    provides methods for calculating observables.


    Instantiation
    -------------
    >>> Event([particle1, particle2, ...])

    """

    def __init__(self,particles=[]):
        self._particles = particles
        self._vn = []


    def _phi(self):
        # a list of phi for each Particle in the Event
        return [p.phi for p in self._particles]


    def _calc_flows(self,vnmin=2,vnmax=6):
        # event-plane method
        phi = np.asarray(self._phi(), dtype='float128')

        for n in range(vnmin,vnmax+1):
            vx = np.mean(np.cos(n*phi))
            vy = np.mean(np.sin(n*phi))
            self._vn.extend([vx,vy])


    def flows(self,vnmin=2,vnmax=6):
        """
        Retrieve the Event's flow coefficients v_n.  Only do the calculation if
        necessary.


        Arguments
        ---------
        vnmin, vnmax -- Range of v_n to calculate.


        Returns
        -------
        [vnmin_x, vnmin_y, ..., vnmax_x, vnmax_y]

        """

        if not self._vn:
            self._calc_flows(vnmin,vnmax)

        return self._vn
