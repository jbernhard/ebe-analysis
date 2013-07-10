"""
An Event is a collection of Particles.
"""


import itertools
import math

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


class Flows:
    """
    Calculate and store flow coefficients v_n.

    Usage
    -----
    >>> Flows(phi,vnmin,vnmax,printvectors=False)

    phi -- array-like object containing the list of phi angles
    vnmin,vnmax -- range of v_n

    optional:
    printvectors -- boolean, whether the string representation is flow vector
        components or flow magnitudes

    """

    def __init__(self,phi,vnmin,vnmax,printvectors=False,sin=np.sin,cos=np.cos):
        # store these as public class attributes
        self.vnmin = vnmin
        self.vnmax = vnmax
        self.printvectors = printvectors

        # init. lists of flow compenents
        self._vx = []
        self._vy = []

        ### use numpy to calculate flows
        # much faster than pure python since phi will typically have size ~10^3

        phi = np.asarray(phi)

        for n in range(self.vnmin,self.vnmax+1):
            nphi = n*phi
            # event-plane method
            self._vx.append( cos(nphi).mean() )
            self._vy.append( sin(nphi).mean() )


    def __str__(self):
        if self.printvectors:
            return ' '.join(map(str,itertools.chain.from_iterable(self.vectors())))
        else:
            return ' '.join(map(str,self.magnitudes()))


    def vectors(self):
        """
        Return an iterable of flow vectors:

        (v_min_x,v_min_y), ..., (v_max_x,v_may_y)

        """

        return zip(self._vx,self._vy)


    def magnitudes(self,sqrt=math.sqrt):
        """
        Return a list of flow magnitudes:

        [v_min, ..., v_max]

        """

        # pure python is faster than numpy for such a small array
        return [sqrt(sum(j**2 for j in i)) for i in self.vectors()]


    def angles(self,atan2=math.atan2):
        """
        Return a list of flow angles:

        [Psi_min, ..., Psi_max]

        """

        return [atan2(y,x) for x,y in self.vectors()]


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
        return [p.phi for p in self._particles]


    def flows(self,vnmin,vnmax,**kwargs):
        """
        Create a Flows object for the Event.

        Arguments
        ---------
        vnmin, vnmax -- range of v_n
        **kwargs -- keyword arguments for instantiating Flows()

        Returns
        -------
        Flows() object

        """

        self._flows = Flows(self._phi(),vnmin,vnmax,**kwargs)

        return self._flows
