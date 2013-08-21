"""
Read event-by-event data via generators.

The lowest-level generator is lines(), which yields lines from stdin, a single
file, or multiple files in sequence.

In the middle are the particle generators particles_from_<format>(), which read
lines and yield Particle objects.  They also yield None to separate events.

The highest-level generator is events_from_files(), which reads from the
particle generators and yields lists of Particle objects, i.e. "events".  It
depends on the particle generators yielding None to know when to separate
events.

All generators take filenames as their primary arguments.
"""


from .particle import *


def open_compressed(filename,mode='rb'):
    """
    Open a file for reading with automatic decompression.  Detects gzip, xz, and
    bz2 files via the file extension.

    Arguments
    ---------
    filename to open

    Returns
    -------
    open file object

    """

    ext = filename.split('.')[-1]

    if ext == 'gz':
        import gzip
        return gzip.open(filename,mode)
    elif ext == 'xz':
        import lzma
        return lzma.open(filename,mode)
    elif ext == 'bz2':
        import bz2
        return bz2.open(filename,mode)
    else:
        return open(filename,mode)


def lines(files=None):
    """
    Read all lines from files or stdin.  A simpler, faster version of
    fileinput.input().

    Everything is read in binary mode, i.e. lines are yielded as bytes objects.
    This is marginally faster than text mode since it avoids an unecessary text
    wrapper.

    Arguments
    ---------
    files -- Filenames to read.  May be an iterable, a single string, or empty.
             If empty or '-', read from stdin.

    Yields
    ------
    lines -- as bytes objects

    """

    if not files or files == '-':
        # read from stdin
        # detach to read in binary mode
        import sys
        yield from sys.stdin.detach()

    elif isinstance(files,str):
        # just one file
        with open_compressed(files) as f:
            yield from f

    else:
        # several files
        for fn in files:
            with open_compressed(fn) as f:
                yield from f


# urqmd particle lines are 435 chars long [including the two chars of '\n']
_urqmd_particle_line_length = 435

# dictionary to convert from urqmd ityp and 2*I3 to monte carlo ID
# adapted from ityp2pdg.f in the urqmd source
# structure is ityp:{2i3:mcid}
_urqmd_particle_dict = {
    # nucleons
    1: {-1: 2112, 1: 2212},
    # N*
    2: {-1: 12112, 1: 12212},
    3: {-1: 1214, 1: 2124},
    4: {-1: 22112, 1: 22212},
    5: {-1: 32112, 1: 32212},
    6: {-1: 2116, 1: 2216},
    7: {-1: 12116, 1: 12216},
    8: {-1: 21214, 1: 22124},
    9: {-1: 42112, 1: 42212},
    10: {-1: 31214, 1: 32124},
    14: {-1: 1218, 1: 2128},
    # Delta
    17: {-3: 1114, -1: 2114, 1: 2214, 3: 2224},
    18: {-3: 31114, -1: 32114, 1: 32214, 3: 32224},
    19: {-3: 1112, -1: 1212, 1: 2122, 3: 2222},
    20: {-3: 11114, -1: 12114, 1: 12214, 3: 12224},
    21: {-3: 11112, -1: 11212, 1: 12122, 3: 12222},
    22: {-3: 1116, -1: 1216, 1: 2126, 3: 2226},
    23: {-3: 21112, -1: 21212, 1: 22122, 3: 22222},
    24: {-3: 21114, -1: 22114, 1: 22214, 3: 22224},
    25: {-3: 11116, -1: 11216, 1: 12126, 3: 12226},
    26: {-3: 1118, -1: 2118, 1: 2218, 3: 2228},
    # Lambda
    27: {0: 3122},
    28: {0: 13122},
    29: {0: 3124},
    30: {0: 23122},
    31: {0: 33122},
    32: {0: 13124},
    33: {0: 43122},
    34: {0: 53122},
    35: {0: 3126},
    36: {0: 13126},
    37: {0: 23124},
    38: {0: 3128},
    39: {0: 23126},
    # Sigma
    40: {-2: 3112, 0: 3212, 2: 3222},
    41: {-2: 3114, 0: 3214, 2: 3224},
    42: {-2: 13112, 0: 13212, 2: 13222},
    43: {-2: 13114, 0: 13214, 2: 13224},
    44: {-2: 23112, 0: 23212, 2: 23222},
    45: {-2: 3116, 0: 3216, 2: 3226},
    46: {-2: 13116, 0: 13216, 2: 13226},
    47: {-2: 23114, 0: 23214, 2: 23224},
    48: {-2: 3118, 0: 3218, 2: 3228},
    # Xi
    49: {-1: 3312, 1: 3322},
    50: {-1: 3314, 1: 3324},
    52: {-1: 13314, 1: 13324},
    # Omega
    55: {0: 3334},
    # gamma
    100: {0: 22},
    # pion
    101: {-2: -211, 0: 111, 2: 211},
    # eta
    102: {0: 221},
    # omega
    103: {0: 223},
    # rho
    104: {-2: -213, 0: 113, 2: 213},
    # f0(980)
    105: {0: 10221},
    # kaon
    106: {-1: 311, 1: 321},
    # eta
    107: {0: 331},
    # k*(892)
    108: {-1: 313, 1: 323},
    # phi
    109: {0: 333},
    # k0*(1430)
    110: {-1: 10313, 1: 10323},
    # a0(980)
    111: {-2: -10211, 0: 10111, 2: 10211},
    # f0(1370)
    112: {0: 20221},
    # k1(1270)
    113: {-1: 10313, 1: 10323},
    # a1(1260)
    114: {-2: -20213, 0: 20113, 2: 20213},
    # f1(1285)
    115: {0: 20223},
    # f1'(1510)
    116: {0: 40223},
    # k2*(1430)
    117: {-1: 315, 1: 325},
    # a2(1329)
    118: {-2: -215, 0: 115, 2: 215},
    # f2(1270)
    119: {0: 225},
    # f2'(1525)
    120: {0: 335},
    # k1(1400)
    121: {-1: 20313, 1: 20323},
    # b1
    122: {-2: -10213, 0: 10113, 2: 10213},
    # h1
    123: {0: 10223},
    # K* (1410)
    125: {-1: 30313, 1: 30323},
    # rho (1450)
    126: {-2: -40213, 0: 40113, 2: 40213},
    # omega (1420)
    127: {0: 50223},
    # phi(1680)
    128: {0: 10333},
    # k*(1680)
    129: {-1: 40313, 1: 40323},
    # rho(1700)
    130: {-2: -30213, 0: 30113, 2: 30213},
    # omega(1600)
    131: {0: 60223},
    # phi(1850)
    132: {0: 337}
}


def _ffloat(x):
    # convert a fortran double to a python float
    # python does not understand 'D' in fortran doubles so replace it with 'E'
    return float(x.replace(b'D',b'E'))


def particles_from_urqmd(files=None):
    """
    Generate Particle objects from UrQMD files.  Yield None to separate events.

    Arguments
    ---------
    files -- list of filenames to read

    Yields
    ------
    Particle() or None

    """

    from math import sqrt, atan2, log

    # use this boolean to keep track of event headers
    # files should begin with a header
    header = True


    for l in lines(files):
        # determine if this is a particle line via its length

        if len(l) == _urqmd_particle_line_length:
            # this is a particle line

            if header:
                # switch out of header mode
                header = False


            # extract necessary values

            # loops are not efficient for only a few calls
            # neither is map()
            # faster to manually call the functions
            # faster to extract values separately than e.g. l.split()

            # momenta
            px = _ffloat(l[121:144])
            py = _ffloat(l[145:168])
            pz = _ffloat(l[169:192])

            # UrQMD ityp and 2*I3
            ityp = int(l[218:221])
            iso = int(l[222:224])

            # determine Monte Carlo ID
            # for antiparticles (ityp<0), negate 2*I3 and MCID
            # checked for speed:  faster than using int(copysign(...))
            sign = 1 if ityp > 0 else -1
            ID = sign * _urqmd_particle_dict[abs(ityp)][sign*iso]

            # transverse momentum
            pT = sqrt(px*px + py*py)

            # azimuthal angle
            phi = atan2(py,px)

            # rapidity
            pmag = sqrt(px*px + py*py + pz*pz)
            eta = 0.5*log((pmag+pz)/max(pmag-pz,1e-10))   # avoid division by zero


            # yield the Particle
            yield Particle(ID,pT,phi,eta)

        else:
            # this is a header line

            if not header:
                # switch to header mode
                header = True
                # yield None to separate events
                yield


def particles_from_std(files=None):
    """
    Generate Particle objects from files containing standard particle info.
    Yield None on blank lines.

    Arguments
    ---------
    files -- list of filenames to read

    Yields
    ------
    Particle() or None

    """

    for l in lines(files):
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
_format_dict = {
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
    filterargs -- key-value pairs for a particle_filter

    Yields
    ------
    events [i.e. sublists of Particles]

    """

    # autodetect input format
    # very simple:  if '.f13' is in the first filename, set format to urqmd
    # else set to std
    if inputformat == 'auto':
        if files and ('.f13' in files or '.f13' in files[0]):
            inputformat = 'urqmd'
        else:
            inputformat = 'std'

    # set the particle generator based on the input format
    particles = _format_dict[inputformat](files)

    # filter particles if necessary
    if any(filterargs.values()):
        particles = filter(particle_filter(**filterargs), particles)

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
