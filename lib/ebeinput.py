"""
Functions for reading event-by-event data.
"""


import fileinput

from .particle import Particle


def particles_from_files(files=None):
    """
    Generate Particle objects from files containing standard particle info.
    Yield None on blank lines.

    Arguments
    ---------
    files -- list of filenames to read, passed directly to fileinput

    Yields
    ------
    Particle() or None

    """

    with fileinput.input(files=files,openhook=fileinput.hook_compressed) as f:

        for l in f:

            # try to unpack the line into standard particle info
            try:
                ID,pT,phi,eta = l.split()

            # exception => this is a blank line
            except ValueError:
                yield

            # line was successfully unpacked => create a Particle
            else:
                yield Particle( int(ID), float(pT), float(phi), float(eta) )


def events_from_particles(particles):
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


def events_from_files(files=None):
    """
    Convenience function to read events directly from files.  Identical to

    >>> events_from_particles(particles_from_files(files))

    """

    return events_from_particles(particles_from_files(files))
