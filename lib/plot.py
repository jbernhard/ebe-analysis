"""

"""


import math

import matplotlib.pyplot as plt
import numpy as np


### plot style options

_figwidth = 10

plt.rc('figure', figsize=[_figwidth,_figwidth/1.618], facecolor='1.0')
plt.rc('font', family='serif')
plt.rc('axes', color_cycle=['#33b5e5','#99cc00','#ff4444','#aa66cc','#ffbb33'])
plt.rc('patch', linewidth=1.5)


def _spectrum(data,n):
    plt.hist(data,
        #bins=math.ceil((data.max()-data.min())/.1),
        bins=int(2*n**.33),
        log=True,
        histtype='step'
    )


def pT(data):
    data = np.asarray(data)

    npart = data.size

    _spectrum(data,npart)

    plt.xlabel(r'$p_T\ \mathrm{[GeV]}$')
    plt.ylabel(r'$1/2\pi p_T \, dN/dp_T$')
    plt.title(r'$p_T\ \mathrm{spectrum\ for}\ ' + str(npart) +
        '\mathrm{\ particles}$')

    plt.show()


def mult(data):
    data = np.asarray(data)

    nev = data.size

    _spectrum(data,nev)

    plt.xlabel(r'$N$')
    plt.ylabel(r'$P(N)$')
    plt.title(r'$\mathrm{multiplicity\ spectrum\ for}\ ' + str(nev) +
        '\mathrm{\ events}$')

    plt.show()


def flows(data):
    data = np.asarray(data)

    try:
        nev,nflow = data.shape
    except ValueError:
        nev = data.size
        nflow = 1

    _spectrum(data,nev)

    plt.xlabel(r'$v_n$')
    plt.ylabel(r'$P(v_n)$')
    plt.title(r'$v_n\ \mathrm{spectrum\ for}\ ' + str(nev) +
        '\mathrm{\ events}$')
    #['column ' + str(i) for i in range(nflow)]
    plt.legend([r'$v_' + str(i) + '$' for i in range(2,2+nflow)])

    plt.show()
