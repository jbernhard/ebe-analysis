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


class BufferedFlows(Flows):
    """
    Subclass of Flows that buffers particles to decrease memory usage at the
    expense of speed.

    A particle object contains an int and three floats, whose C-types total 28
    bytes of memory.  However Python objects have some overhead:  a real-world
    test showed about 175 bytes per particle.  This means 1 GiB (2^30 bytes) of memory
    can hold ~6e6 paricles.  Assuming ~1e4 particles per event, that's ~600
    events per GiB of memory.

    So this class is useful for average/differential flows over many (>10^3) events.

    The buffering calculation introduces very slight (~10^-16) floating-point
    errors.

    Usage
    -----
    Create an instance via

    >>> BufferedFlows(vnmin,vnmax)

    where vnmin,vnmax have the usual meaning.

    The optional argument 'bufsize' specifies the number of particles to hold in
    the buffer, default 100000.  This should always be set as high as possible.
    Calculating flows for an 8571-particle test event took 9.05, 11.4, 31.6,
    231, and 2180 ms, for bufsizes of 10000, 1000, 100, 10, and 1, respectively.
    The same event with Flows.from_event() took 4.49 ms.

    After creating the object, give it particles via the add_particle() method.

    When finished adding particles, call the update() method to flush the
    buffer.  Then the object may be used as a regular flows object.

    """

    def __init__(self,vnmin,vnmax,bufsize=100000):
        assert bufsize > 0

        # init. the buffer
        self._buffer = []
        self._bufsize = bufsize

        # store attributes
        self.vnmax = vnmax
        self.vnmin = vnmin

        # init. vars. which will be modified later
        self.multiplicity = 0
        self.vx = [0.0 for _ in range(vnmin,vnmax+1)]
        self.vy = [0.0 for _ in range(vnmin,vnmax+1)]


    def add_particle(self,particle):
        """
        Add a particle to the buffer.

        Automatically flushes the buffer if it has reached maximum size.

        """

        self._buffer.append(particle)

        if len(self._buffer) >= self._bufsize:
            self.update()


    def update(self):
        """
        Flush the buffer and update flow vectors.

        """

        # ensure the buffer isn't empty
        # otherwise we get nan
        if len(self._buffer) > 0:
            # numpy array of angles
            phi = array([p.phi for p in self._buffer])

            # multiplicity of the buffer
            mult_buffer = len(self._buffer)

            # total multiplicity
            mult_total = self.multiplicity + mult_buffer

            # update flow vectors via the multiplicity-weighted average of the
            # existing vector and the buffer's vector
            # pure python is faster than numpy for such small vectors
            for k,n in enumerate(range(self.vnmin,self.vnmax+1)):
                nphi = n*phi

                self.vx[k] = (self.multiplicity*self.vx[k] +
                        mult_buffer*cos(nphi).mean())/mult_total

                self.vy[k] = (self.multiplicity*self.vy[k] +
                        mult_buffer*sin(nphi).mean())/mult_total

            # update multiplicity
            self.multiplicity = mult_total

            # flush buffer
            self._buffer = []
