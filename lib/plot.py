"""

"""


import math

import matplotlib.pyplot as plt
import numpy as np


### plot style options

_figwidth = 14

plt.rc('figure', figsize=[_figwidth,_figwidth/1.618], facecolor='1.0')
plt.rc('font', family='serif')
plt.rc('axes', color_cycle=['#33b5e5','#99cc00','#ff4444','#aa66cc','#ffbb33'])
plt.rc('lines', linewidth=1.5)
plt.rc('patch', linewidth=1.5)



def pT(data,nev=1,bins=None,log=True):
    data = np.asarray(data)

    counts, edges = np.histogram(data,bins=bins or int(2*data.size**.33))
    centers = (edges[1:] + edges[:-1])/2

    if nev > 1:
        counts /= nev

    cmd = plt.semilogy if log else plt.plot
    cmd(centers,counts)

    npart = data.size

    plt.xlabel(r'$p_T\ [\mathrm{GeV}]$')
    plt.ylabel(r'$1/2\pi p_T \, dN/dp_T\ [\mathrm{GeV}^{-2}]$')
    plt.title(str(nev) + ' events / ' + str(npart) + ' particles')

    plt.show()


def flows(data,vnmin=2,bins=None,log=True):
    data = np.asarray(data).T

    try:
        nflow,nev = data.shape
    except ValueError:
        nev = data.size
        nflow = 1

    for n in range(nflow):
        counts, edges = np.histogram(data[n],bins=bins or int(2*nev**.33),
                density=True)
        centers = (edges[1:] + edges[:-1])/2
        cmd = plt.semilogy if log else plt.plot
        cmd(centers,counts,label=r'$v_' + str(n+vnmin) + '$')

    for n in ['2','3']:
        vn,pvn,stat,syshigh,syslow = np.loadtxt(
            '/home/jonah/qcd/ebe/data/v' + n + '_0-5.dat', unpack=True, skiprows=1
        )

        yerr = [np.sqrt(np.square(stat)+np.square(syslow)), np.sqrt(np.square(stat)+np.square(syshigh))]

        plt.errorbar(vn, pvn, yerr=yerr, fmt={'2':'o','3':'s'}[n],
                label=r'$\mathrm{ATLAS}\ v_' + n + '$', ms=5, lw=1)

    plt.xlabel(r'$v_n$')
    plt.ylabel(r'$P(v_n)$')
    plt.title(r'$v_n\ \mathrm{spectra\ for}\ ' + str(nev) +
        '\mathrm{\ events}$')
    plt.legend()

    plt.show()


"""


def flows(data):
    data = np.asarray(data)

    try:
        nev,nflow = data.shape
    except ValueError:
        nev = data.size
        nflow = 1

    plt.hist(data,
        bins=int(2*nev**.33),
        log=True,
        histtype='step',
        normed=True,
        label=[r'$v_' + str(i) + '$' for i in range(2,2+nflow)]
    )

    plt.xlabel(r'$v_n$')
    plt.ylabel(r'$P(v_n)$')
    plt.title(r'$v_n\ \mathrm{spectrum\ for}\ ' + str(nev) +
        '\mathrm{\ events}$')
    #['column ' + str(i) for i in range(nflow)]
    #plt.legend([r'$v_' + str(i) + '$' for i in range(2,2+nflow)])
    plt.legend()

    plt.show()
"""


"""
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
"""
