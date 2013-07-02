"""
Provides an interface to PDG particle information.
"""


import os.path
import sqlite3
import urllib.request


# database where PDG data will be stored, relative to this file's location
dbname = 'pdg.db'

# URL of PDG file containing particle info
pdgurl = 'http://pdg.lbl.gov/2012/mcdata/mass_width_2012.mcd'

#       1   contains either "M" or "W" indicating mass or width
#  2 -  9 \ Monte Carlo particle numbers as described in the "Review of
# 10 - 17 | Particle Physics". Charge states appear, as appropriate,
# 18 - 25 | from left-to-right in the order -, 0, +, ++.
# 26 - 33 / 
#      34   blank
# 35 - 49   central value of the mass or width (double precision)
#      50   blank
# 51 - 58   positive error
#      59   blank
# 60 - 67   negative error
#      68   blank
# 69 - 89   particle name left-justified in the field and
#           charge states right-justified in the field.
#           This field is for ease of visual examination of the file and
#           should not be taken as a standardized presentation of
#           particle names.


class PDG:
    """
    Creates and reads a sqlite DB of the PDG particle table.

    Usage
    -----
    >>> pdg = PDG()

    This opens a connection to the DB.  If the DB does not exist, it is
    created.

    Then, call a public method, e.g. to retrieve the IDs of all charged
    particles
    >>> pdg.chargedIDs()
    [int, int, ...]

    """

    def __init__(self):
        # full path to DB is the directory of this file + DB filename
        self._dbfile = os.path.join(os.path.dirname(__file__),dbname)

        # init. class vars.
        self._charged = None

        # need to create the DB if it doesn't exist
        shouldmakedb = not os.path.exists(self._dbfile)

        # open a connection to the DB
        self._conn = sqlite3.connect(self._dbfile)

        if shouldmakedb:
            self._makedb()


    def __del__(self):
        # commit any remaining changes and close the connection
        self._conn.commit()
        self._conn.close()


    def _makedb(self):
        # create a SQL table to hold particle info
        self._conn.execute('create table particles \
            (id INT,mass DOUBLE,name VARCHAR(30),charge VARCHAR(5))')

        # create a row for each particle via the _getparticles generator
        self._conn.executemany('insert into particles \
            (id,mass,name,charge) values (?,?,?,?)', self._getparticles())

        # commit changes
        self._conn.commit()


    def _getparticles(self):
        # download the PDG particle table and generate tuples
        # (ID,mass,name,charge) for each particle
        with urllib.request.urlopen(pdgurl) as f:
            for l in f:
                # mass lines only
                if l[0:1] == b'M':

                    # extract ID(s)
                    ID = []
                    for i in [2,10,18,26]:
                        j = l[i:i+7]
                        if j.strip():
                            ID.append(int(j))

                    # mass
                    mass = float(l[35:49])

                    # name and charge(s)
                    name,charge = l[68:89].decode().split()
                    charge = charge.split(',')

                    ### unnecessary...
                    ## convert charge(s) to numbers
                    #charge = [{'-': -1,
                    #    '-1/3': float(-1/3),
                    #    '0': 0,
                    #    '+2/3': float(2/3),
                    #    '+': 1,
                    #    '++': 2}[x] for x in charge.split(',')]

                    # treat each ID/charge as a separate particle
                    for k in range(len(ID)):
                        yield ID[k],mass,name,charge[k]


    def charged(self):
        """
        Retrieve the IDs of all charged particles.

        Returns
        -------
        list of integers

        """

        if not self._charged:
            self._charged = [row[0] for row in self._conn.execute('select id from particles where charge != 0')]

        return self._charged
