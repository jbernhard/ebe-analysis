#!/usr/bin/env python3

import urllib.request
import sqlite3


### PDG file containing particle info
pdgurl = 'http://pdg.lbl.gov/2012/mcdata/mass_width_2012.mcd'

# format
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


def particles():
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


def main():

    conn = sqlite3.connect('particles.db')
    c = conn.cursor()
    
    c.execute('drop table if exists particles')
    c.execute('create table particles (id INT,mass DOUBLE,name VARCHAR(30),charge VARCHAR(5))')

    c.executemany('insert into particles (id,mass,name,charge) values (?,?,?,?)', particles())

    conn.commit()
    c.close()



if __name__ == "__main__":
    main()
