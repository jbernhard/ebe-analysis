"""
docstring
"""


import numpy as np


class Batch:
    def __init__(self,events=[]):
        self._events = events

    def add_event(self,event):
        self._events.append(event)

    def events(self):
        return self._events
