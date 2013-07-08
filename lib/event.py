"""
An Event is a collection of Particles.
"""


import numpy as np

from .particle import Particle


def frominput(iterable):
    """
    Generate Events from standard particle info.

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

        if l.isspace():
            # this is a blank line => have reached the end of this event
            if particles:
                yield Event(particles)
                particles = []

        else:
            # this is a particle line
            ID,pT,phi,eta = l.split()

            # create a new Particle and add it to the list
            particles.append(Particle(
                    ID=int(ID),
                    pT=float(pT),
                    phi=float(phi),
                    eta=float(eta)
                )
            )

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

    Iterating over an Event is equivalent to iterating over its Particles, e.g.

    >>> e = Event([p1,p2,p3])
    >>> [p for p in e]
    [p1,p2,p3]

    The length of an Event is defined as its number of Particles:

    >>> len(e)
    3

    """

    def __init__(self,particles=[]):
        self._particles = particles

    def __iter__(self):
        return iter(self._particles)

    def __len__(self):
        return len(self._particles)


    def _phi(self):
        # phi of each Particle in the Event
        return np.array([p.phi for p in self._particles])


    def flows(self,vnmin,vnmax,mean=np.mean,sin=np.sin,cos=np.cos):
        """
        Calculate the Event's flow coefficients v_n.

        Arguments
        ---------
        vnmin, vnmax -- range of v_n to calculate

        Returns
        -------
        [vnmin_x, vnmin_y, ..., vnmax_x, vnmax_y]

        """

        self._vn = []

        phi = self._phi()

        for n in range(vnmin,vnmax+1):
            # event-plane method
            nphi = n*phi
            vx = mean(cos(nphi))
            vy = mean(sin(nphi))
            self._vn.extend([vx,vy])

        return self._vn
