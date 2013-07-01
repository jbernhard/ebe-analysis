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

    """

    def __init__(self,events=[]):
        self._events = events
