# EbE analysis

Tools for analyzing event-by-event heavy-ion collision simulation data.


## Design principles

  * Unix-style tools, i.e. small executables designed to gracefully accomplish a single task.  Tools should interface with each other seamlessly.
  * Clean, consistent, thoroughly commented pythonic code.
  * Flexible input:  read from stdin or files on disk, handle compressed (gzip/bzip2) files transparently.  Accomplished via Python's
    [fileinput](http://docs.python.org/3/library/fileinput.html) module.
  * Separate, modular worker functions.
  * Minimal dependencies:  python3 + numpy/scipy.  Optional:  matplotlib for plotting.
