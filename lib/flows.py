"""
Calculate and store flow coefficients.

The main implementation of the module is the Flows class.  Several functions
exist for processing batches of events:

    event_by_event() -- creates a Flows for each event independently
    average() -- creates a single Flows averaged over all events
    differential() -- creates Flows by pT bin, averaged over all events

"""


import itertools
import math

import numpy as np


def event_by_event(events,vnmin,vnmax):
    """
    Calculate flows event-by-event.

    Arguments
    ---------
    events -- iterable of events
    vnmin,vnmax -- range of v_n

    Yields
    ------
    Flows -- for each event

    """

    for e in events:
        yield Flows(e,vnmin,vnmax)


def average(events,vnmin,vnmax):
    """
    Calculate average flows for a set of events.

    Arguments
    ---------
    events -- iterable of events
    vnmin,vnmax -- range of v_n
    buffer -- boolean [optional, default True]

    Returns
    -------
    Flows

    """

    fl = Flows(None,vnmin,vnmax)

    for e in events:
        fl.add_event(e)

    return fl


def differential(events,vnmin,vnmax,width=.1,bufsize=100000,floor=math.floor):
    """
    Calculate average differential (pT) flows for a set of events.

    Particles can be processed in chunks ("buffered") to reduce memory usage.
    Buffering is on by default and may be disable by setting the bufsize
    argument to any false value.  Beware:  without buffering, all particles must
    be loaded into memory.

    Buffering may have an impact on speed.  To wit, the following benchmarks,
    with vnmin,vnmax = 2,3 and bufsize = 1000000 [the default] or None
    [buffering off].

    no. events  |  no. particles  |  buffering  |  no buffering
    -----------------------------------------------------------
             1  |          9,472  |    10.4 ms  |       15.0 ms
            10  |         94,782  |    75.8 ms  |       86.8 ms
           100  |        943,262  |     816 ms  |        819 ms
          1000  |      9,466,762  |    8100 ms  |       8460 ms

    So buffering is actually faster for very large numbers of events.  Not to
    mention, 1000 events without buffering requires ~1.5 GiB of memory.


    Arguments
    ---------
    events -- iterable of events
    vnmin,vnmax -- range of v_n
    width -- width of p_T bins in GeV [optional, default 0.1]
    bufsize -- particle buffer size [optional, default 100000]

    Yields
    ------
    pT_mid, Flows -- for each pT bin,
                     where pT_mid is the middle pT value of the bin

    """

    # flatten events
    particles = itertools.chain.from_iterable(events)

    # buffer particles
    if bufsize:
        flows = []
        subevents = []

        zip_longest = itertools.zip_longest

        # trick to split an iterable into chunks
        # taken from itertools recipes in the std. lib. docs
        # once the iterable is exhausted, this will yield None
        for buf in zip_longest(*[particles]*bufsize):
            for p in buf:
                try:
                    # pT index of Particle
                    idx = floor(p.pT/width)
                except AttributeError:
                    # this is None, not a Particle
                    break
                else:
                    # ask forgiveness, not permission
                    while True:
                        try:
                            # add particle to appropriate subevent
                            subevents[idx].append(p)
                        except IndexError:
                            # create subevents as needed
                            subevents.append([])
                        else:
                            break


            # calculate flows for each subevent
            # then clear subevents and proceed to next chunk
            for f,s in zip_longest(flows,subevents):
                try:
                    f.add_event(s)
                except AttributeError:
                    flows.append(Flows(s,vnmin,vnmax))
                s.clear()

    # no buffering
    else:
        subevents = []

        for p in particles:
            # ask forgiveness, not permission
            while True:
                try:
                    # add particle to appropriate subevent
                    subevents[floor(p.pT/width)].append(p)
                except IndexError:
                    # create subevents as needed
                    subevents.append([])
                else:
                    break

        # calculate flows for each subevent
        flows = (Flows(e,vnmin,vnmax) for e in subevents)


    # return (pT_mid,Flows) for each bin
    # round pT_mid to remove annoying floating-point errors
    return ((round((2*i+1)/2*width,10), f) for i,f in enumerate(flows))


class Flows:
    """
    Calculates and stores flow coefficients and provides related methods.

    Uses numpy for large arrays and pure python for small lists.

    Arguments
    ---------
    event -- list of particles
    vnmin,vnmax -- range of v_n

    If the event is any false value, the instance will be created with all flows
    set to zero.  Events can be added later with add_event().

    """

    def __init__(self,event,vnmin,vnmax):
        assert vnmax >= vnmin > 0

        # store attributes
        self.vnmin = vnmin
        self.vnmax = vnmax
        self.multiplicity = 0

        # init. flow vectors
        self.vx = [0.0] * (vnmax - vnmin + 1)
        self.vy = [0.0] * (vnmax - vnmin + 1)

        self.add_event(event)


    def add_event(self,event,array=np.array,cos=np.cos,sin=np.sin):
        """
        Add an event to the current flows.  Mainly useful for building up
        average/differential flows in pieces.

        For example, given a set of 100,000 particles, the flows can be
        calculated all at once, or in 10 chunks of 10,000.

        If the event is any false value, silently do nothing.

        Arguments
        ---------
        event -- list of particles

        """

        if event:
            # multiplicity of new event
            mult_event = len(event)

            # total multiplicity
            mult_total = self.multiplicity + mult_event

            # numpy array of angles
            phi = array([p.phi for p in event])

            ### update flow vectors
            # multiplicity-weighted average of
            # the existing vector and the new event's vector
            for k,n in enumerate(range(self.vnmin,self.vnmax+1)):
                nphi = n*phi

                self.vx[k] = (self.multiplicity*self.vx[k] +
                        mult_event*cos(nphi).mean())/mult_total

                self.vy[k] = (self.multiplicity*self.vy[k] +
                        mult_event*sin(nphi).mean())/mult_total

            # update multiplicity
            self.multiplicity = mult_total


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
        return itertools.chain.from_iterable(self.vectors())


    def magnitudes(self,sqrt=math.sqrt):
        """
        Return an iterable of flow magnitudes:

        v_min, ..., v_max

        """

        return (sqrt(x*x + y*y) for x,y in self.vectors())


    def angles(self,atan2=math.atan2):
        """
        Return an iterable of flow angles:

        Psi_min, ..., Psi_max

        """

        return (atan2(y,x) for x,y in self.vectors())
