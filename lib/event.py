"""
An Event is a collection of Particles.
"""


import numpy as np
from .particle import Particle


def frominput(iterable):
    """
    Generate Events from standard particle info, such as is output by
    urqmd.tostdout().

    Arguments
    ---------
    iterable -- containing standard particle lines [bytes or strings]

    Yields
    ------
    Event()

    """

    # init. empty list of particles
    particles = []

    # scan through lines
    for l in iterable:
        # if l is a blank line, then l.strip() will be an empty string

        if l.strip():
            # this is a particle line
            # instantiate a new Particle and add it to the list

            # standard order is ID,pT,phi,eta
            fields = l.split()
            particles.append(Particle(
                    ID=int(fields[0]),
                    pT=float(fields[1]),
                    phi=float(fields[2]),
                    eta=float(fields[3])
                )
            )

        else:
            # empty line => yield current event, initialize new one
            if particles:
                yield Event(particles)
                particles = []

    # lines have been exhausted
    # typically there will be one last event to yield
    if particles:
        yield Event(particles)



class Event:
    """
    Stores a list of Particles and provides methods for calculating observables.

    Usage
    -----
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
