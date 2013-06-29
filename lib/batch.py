"""
A Batch is a collection of Events.
"""


import numpy as np


class Batch:
    """
    The implementation of the module.  It stores a list of Events.


    Instantiation
    -------------
    >>> Batch([event1, event2, ...])

    """

    def __init__(self,events=[]):
        self._events = events
