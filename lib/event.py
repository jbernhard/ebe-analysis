"""
docstring
"""


import numpy as np


class Event:
    def __init__(self,particles=[]):
        self._particles = particles
        self._vn = []


    def _phi(self):
        return [p.phi() for p in self._particles]


    def particles(self):
        return self._particles


    def add_particle(self,particle):
        self._particles.append(particle)


    def calculate_flows(self,vnmin=2,vnmax=6):
        if not self._vn:
            phi = np.asarray(self._phi(), dtype='float128')

            for n in range(vnmin,vnmax+1):
                vx = np.mean(np.cos(n*phi))
                vy = np.mean(np.sin(n*phi))
                self._vn.extend([vx,vy])

        return self._vn
