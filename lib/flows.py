"""
Classes for calculating and storing flow coefficients.
"""


from itertools import chain
from math import atan2, sqrt

from numpy import array, cos, sin


def flow_function(vnmin,vnmax,method='magnitudes'):
    """
    Factory function:  create a flow-calculator function for use with events.

    This is useful for calculating flows the exact same way on a large number of
    events.

    Arguments
    ---------
    vnmin,vnmax -- range of v_n
    method -- the method of Flows which should be called

    Returns
    -------
    function of events

    Example:
    >>> flowcalc = flow_function(vnmin,vnmax,'magnitudes')
    >>> for e in events:
            flowcalc(e)

    """

    def f(event):
        return getattr(Flows.from_event(event,vnmin,vnmax),method)()

    return f


class Flows:
    """
    Store flow coefficients and provide related methods.

    Arguments
    ---------
    vx,vy -- lists of flow vector components
    vnmin,vnmax -- range of v_n
    multiplicity -- event multiplicity

    """

    def __init__(self,vx=[],vy=[],vnmin=0,vnmax=0,multiplicity=0):
        # sanity check
        assert len(vx) == len(vy) == vnmax - vnmin + 1

        # store attributes
        self.vx = tuple(vx)
        self.vy = tuple(vy)
        self.vnmin = vnmin
        self.vnmax = vnmax
        self.multiplicity = multiplicity


    @classmethod
    def from_event(cls,event,vnmin,vnmax):
        """
        Alternate constructor for Flows.  Calculates flow vectors directly from
        an event.

        Arguments
        ---------
        event -- list of particles
        vnmin,vnmax -- range of v_n

        """

        multiplicity = len(event)

        if multiplicity < 2:
            # flow doesn't make sense with too few particles
            # in this case, set all flows to zero
            vx = [0.0] * (vnmax - vnmin + 1)
            vy = [0.0] * (vnmax - vnmin + 1)

        else:
            # init. lists of flow compenents
            vx = []
            vy = []

            ### use numpy to calculate flows
            # much faster than pure python since phi will typically have size ~10^3

            phi = array([p.phi for p in event])

            for n in range(vnmin,vnmax+1):
                nphi = n*phi
                # event-plane method
                vx.append( cos(nphi).mean() )
                vy.append( sin(nphi).mean() )

        return cls(vx,vy,vnmin,vnmax,multiplicity)


    def vectors(self):
        """
        Return an iterable of flow vectors:

        (v_min_x,v_min_y), ..., (v_max_x,v_may_y)

        """

        return zip(self.vx,self.vy)


    def vectorchain(self):
        """
        Return an iterable of flattened flow vectors:

        v_min_x, v_min_y, ..., v_max_x, v_may_y

        """
        return chain.from_iterable(self.vectors())


    def magnitudes(self):
        """
        Return an iterable of flow magnitudes:

        v_min, ..., v_max

        """

        # pure python is faster than numpy for such a small array
        return (sqrt(x*x + y*y) for x,y in self.vectors())


    def angles(self):
        """
        Return an iterable of flow angles:

        Psi_min, ..., Psi_max

        """

        return (atan2(y,x) for x,y in self.vectors())
