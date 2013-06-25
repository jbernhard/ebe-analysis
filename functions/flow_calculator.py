"""
Calculates flow coefficients v_n from standard particle information.

Typical usage:

>>> import flow_calculator
>>> vn = flow_calculator.calculate_vn(event)
"""


import numpy as np



def calculate_vn(event,vnmin=2,vnmax=6):
    """Calculate flow coefficients.

    Arguments:
    event -- Array-like.  Each row must contain standard particle info.  Will
    accept multiple events concatenated together, but note that all data must be
    read into memory.

    Keyword arguments:
    vnmin, vnmax -- range of v_n to calculate

    Returns:
    [vnmin_x, vnmin_y, ..., vnmax_x, vnmax_y]

    """

    #pT,phi,eta = np.loadtxt(event, usecols=(1,2,3), unpack=True)
    #pT,phi,eta = np.asarray(event, dtype='float128').T[1:]

    # extract phi from event input
    phi = np.asarray([i[2] for i in event], dtype='float128')

    vn = []

    # calculate the requested vn
    for n in range(vnmin,vnmax+1):
        vx = np.mean(np.cos(n*phi))
        vy = np.mean(np.sin(n*phi))
        vn.extend([vx,vy])

    return vn
