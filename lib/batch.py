"""
A Batch is a collection of Events.
"""


import numpy as np


class Batch:
    """
    Stores a list of Events.

    Usage
    -----
    >>> Batch([event1, event2, ...])

    Iterating over a Batch is equivalent to iterating over its Events, e.g.

    >>> b = Batch([e1,e2,e3])
    >>> [e for e in b]
    [e1,e2,e3]

    The length of a Batch is defined as its number of Events:

    >>> len(b)
    3

    """

    def __init__(self,events=[]):
        self._events = events

    def __iter__(self):
        return iter(self._events)

    def __len__(self):
        return len(self._events)
