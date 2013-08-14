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

    def __init__(self,phi,vnmin,vnmax,printvectors=False,minparticles=10,
            sin=np.sin,cos=np.cos):
        # store these as public class attributes
        self.vnmin = vnmin
        self.vnmax = vnmax
        self.printvectors = printvectors
        self.minparticles = minparticles

        if len(phi) < self.minparticles:
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


    def _pT(self):
        # pT of each Particle in the Event
        return [p.pT for p in self._particles]

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


    def pTsubevents1(self,width,floor=math.floor):
        for pT,particles in itertools.groupby(
                sorted(self._particles, key=lambda x: x.pT),
                #lambda x: round(0.5*(2*floor(x.pT/width)+1)*width,8)
                lambda x: 0.5*(2*floor(x.pT/width)+1)*width
                ):
            yield pT,Event(list(particles))


    def pTsubevents2(self,width,floor=math.floor):
        return ( (pT, Event(list(particles))) for pT,particles in itertools.groupby(
                sorted(self._particles, key=lambda x: x.pT),
                #lambda x: round(0.5*(2*floor(x.pT/width)+1)*width,8)
                lambda x: 0.5*(2*floor(x.pT/width)+1)*width
                ) )


    def pTsubevents3(self,width,floor=math.floor,ceil=math.ceil):
        """
        Split the event into multiple subevents by pT bin.

        Arguments
        ---------
        width -- of each pT bin

        Returns
        -------
        pT_mid, Event() -- for each pT bin

        pT_mid = middle pT value of the bin
        Event() = corresponding subevent

        """

        ### create pT bins with specified width

        # calculate required number of bins
        pTmax = max(self._pT())
        nbin = ceil(pTmax/width)

        # create an empty list for each bin
        bins = [[] for i in range(nbin)]


        ### sort particles into bins
        for p in self._particles:
            bins[floor(p.pT/width)].append(p)


        ### return (pT_mid, Event()) for each bin
        # round pT_mid to avoid floating point errors
        return ( (round(0.5*(2*n+1)*width,6), Event(particles))
                for n,particles in enumerate(bins) )


    def pTsubevents4(self,width,floor=math.floor,ceil=math.ceil):

        maxpT = max(self._particles, key=lambda x: x.pT).pT

        #subevents = {}
        #lower = 0
        #while lower < maxpT:
        #    subevents[lower+width/2] = []
        #    lower += width
        subevents = {round((2*n+1)*width/2,8): [] for n in range(ceil(maxpT/width))}

        for p in self._particles:
            subevents[round((2*floor(p.pT/width)+1)*width/2,8)].append(p)

        return ((pT,Event(particles)) for pT,particles in
                sorted(subevents.items()))
