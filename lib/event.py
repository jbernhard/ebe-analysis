"""
An Event is a collection of Particles.
"""


import itertools
import math

import numpy as np

from . import particle


def from_files(files=None):
    """
    Convenience function to read events directly from files.  Identical to

    >>> from_particles(particle.from_files(files))

    """

    return from_particles(particle.from_files(files))


def from_particles(particles):
    """
    Generate events (lists of particles) by splitting an iterable of particles
    into sublists.

    Arguments
    ---------
    particles -- iterable containing Particle objects

    Yields
    ------
    sublists of Particles

    """

    # init. empty event
    event = []

    for p in particles:

        if p:
            # append valid particles to the current event
            event.append(p)

        else:
            # have reached the end of the this event
            # yield current event and init. a new one
            if event:
                yield event
                event = []

    # particles have been exhausted
    # typically there will be one last event to yield
    if event:
        yield event


class Flows:
    """
    Calculate and store flow coefficients v_n for an event.

    Usage
    -----
    >>> Flows(event,vnmin,vnmax)

    event -- list of Particle objects
    vnmin,vnmax -- range of v_n

    """

    def __init__(self,event,vnmin,vnmax,sin=np.sin,cos=np.cos):
        # store these as public class attributes
        self.vnmin = vnmin
        self.vnmax = vnmax
        self.npart = len(event)

        if self.npart < 2:
            # flow doesn't make sense with too few particles
            # in this case, set all flows to zero
            self._vx = [0.0] * (self.vnmax - self.vnmin + 1)
            self._vy = [0.0] * (self.vnmax - self.vnmin + 1)

        else:
            # init. lists of flow compenents
            self._vx = []
            self._vy = []

            ### use numpy to calculate flows
            # much faster than pure python since phi will typically have size ~10^3

            phi = np.fromiter((p.phi for p in event), float, count=self.npart)

            for n in range(self.vnmin,self.vnmax+1):
                nphi = n*phi
                # event-plane method
                self._vx.append( cos(nphi).mean() )
                self._vy.append( sin(nphi).mean() )


    def vectors(self):
        """
        Return an iterable of flow vectors:

        (v_min_x,v_min_y), ..., (v_max_x,v_may_y)

        """

        return zip(self._vx,self._vy)


    def vectorchain(self):
        """
        Return an iterable of flattened flow vectors:

        v_min_x, v_min_y, ..., v_max_x, v_may_y

        """
        return itertools.chain.from_iterable(self.vectors())


    def magnitudes(self,sqrt=math.sqrt):
        """
        Return an iterable of flow magnitudes:

        v_min, ..., v_max

        """

        # pure python is faster than numpy for such a small array
        return (sqrt(x*x + y*y) for x,y in self.vectors())


    def angles(self,atan2=math.atan2):
        """
        Return an iterable of flow angles:

        Psi_min, ..., Psi_max

        """

        return (atan2(y,x) for x,y in self.vectors())
