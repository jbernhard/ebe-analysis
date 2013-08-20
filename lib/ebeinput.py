"""
Functions for reading event-by-event data.
"""


import fileinput

from .particle import Particle, particlefilter
from .urqmd import particles_from_urqmd


def particles_from_std(files=None):
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


# map input format strings to particle generators
_formatdict = {
    'std'   : particles_from_std,
    'urqmd' : particles_from_urqmd
}


def events_from_files(files=None,inputformat='auto',**filterargs):
    """
    Generate events (lists of particles) by splitting an iterable of particles
    into sublists.

    Arguments
    ---------
    files -- list of filenames to read
    inputformat -- 'std' or 'urqmd'
    filterargs -- key-value pairs for a particlefilter

    Yields
    ------
    events [i.e. sublists of Particles]

    """

    # autodetect input format
    # very simple:  if '.f13' is in the first filename, set format to urqmd
    # else set to std
    if inputformat == 'auto' and files and ('.f13' in files or '.f13' in files[0]):
        inputformat = 'urqmd'
    else:
        inputformat = 'std'

    # set the particle generator based on the input format
    particles = _formatdict[inputformat](files)

    # filter particles if necessary
    if any(filterargs.values()):
        particles = filter(particlefilter(**filterargs), particles)

    # init. empty event
    event = []

    # process each particle
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
