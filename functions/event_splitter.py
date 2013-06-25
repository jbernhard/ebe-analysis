"""
Split events separated by blank lines into separate objects.

Typical usage:

>>> import event_splitter
>>> with open(file) as f:
        for event in event_splitter.splitter(f):
            process(event)
"""


def splitter(iterable):
    """
    input:  several events concatenated together but separated by one or more blank lines
    output:  yields single events, one at a time
    """

    """Split events into separate objects.  Yield one event at a time.

    Arguments:
    iterable -- object containing standard particle lines [bytes or strings]

    Yields:
    event -- 2D python list; each row contains standard particle info

    """

    event = []

    # scan through lines
    for l in iterable:
        # if l is a blank line, then l.strip() will be an empty string

        if l.strip():
            # this is a particle line => add it to the event
            event.append(l.split())

        else:
            # empty line => yield current event, initialize new one
            if event:
                yield event
                event = []

    # lines have been exhausted
    # typically there will be one last event to yield
    if event:
        yield event
