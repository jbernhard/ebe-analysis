# EbE analysis

Tools for analyzing event-by-event heavy-ion collision simulation data.



## Design

* **Unix-style tools:**
Each executable is a small Python script designed to gracefully accomplish a single task.

* **Flexible input:**
Executables read from stdin or files on disk.  Compressed files (gzip/bzip2) are handled transparently.

* **Output to stdout:**
Results are printed to stdout as they are calculated.  This allows the user to choose file names, pass through gzip/bz2, etc.  Executables can
interface with each other via shell pipes.

* **Modular worker classes:**
Most of the real work occurs in the classes located in `lib/`.  This makes it trivial to reuse functionality.

* **Three fundamental classes:**
  * Particle:  Each instance of this class corresponds to an actual particle.  It stores physical properties.
  * Event:  Stores a list of Particles and provides methods for calculating event-by-event observables.  [This class is currently only partially implemented.]
  * Batch:  Stores a list of Events and provides relevant methods.  [This class is not currently implemented.]

* **Standard particle information:**
Each particle is represented by four quantities:  Monte Carlo ID, pT, phi, eta.  This allows roughly a 75% reduction in size compared to raw UrQMD files.

* **Minimal dependencies:**
Python 3 and numpy.



## Usage

Executables are located in the root directory and prefixed with `ebe-`.  I recommend adding this directory to your path; the following examples assume that you
have.  All executables have built-in usage information, accessible via the `-h/--help` command-line switch.

### Reading events

`ebe-read` is the event reader.  It parses UrQMD files and outputs standard particle information with events separated by blank lines.

Assume `0.f13.gz`, `1.f13.gz` are gzipped UrQMD files containing one or more events.  The following commands are equivalent:

    ebe-read 0.f13.gz 1.f13.gz
    zcat 0.f13.gz 1.f13.gz | ebe-read
    gzip -d 0.f13.gz 1.f13.gz && ebe-read 0.f13 1.f13

Shell globbing works normally.  For example, this reads all gzipped UrQMD files in the current directory:

    ebe-read *.f13.gz

Basic particle filtering is implemented; e.g. to output only pions:

    ebe-read [files] --ID 111 211

The `--ID` option may be passed before the filenames along with a `--` to indicate the end of options:

    ebe-read --ID 111 211 -- [files]

Otherwise, the filenames will be interpreted as IDs.

This will select charged particles with pT > 0.5 GeV and |eta| < 2.5:

    ebe-read --charged --pTmin 0.5 --etamax 2.5

### Calculating flow coefficients

`ebe-flows` is the flow calculator.  It reads standard particle information and calculates flow vectors event-by-event using the single-particle event-plane method.
The following are equivalent:

    ebe-read [files] | ebe-flows
    ebe-read [files] | gzip > events.dat.gz && ebe-flows events.dat.gz

The default range of v\_n is 2-6.  This may be customized via the `--vn` option, e.g. `ebe-flows --vn 2 6`.

Flows are output in the format

    vn_min_x vn_min_y ... vn_max_x vn_max_y

### Calculating multiplicities

`ebe-multiplicity` reads standard particle information and outputs the multiplicities of each event.  This is useful e.g. to calculate midrapidity yields:

    ebe-read --charged --etamax 0.5 | ebe-multiplicity

With the `--stats` option, the mean and standard deviation are also calculated.  They are printed to stderr [not stdout] on the final line.  This allows the EbE
multiplicities to be separated from the stats, e.g.

    ebe-multiplicity --stats > /dev/null

will output _only_ the stats.



## Planned features

* **Improved flow calculations:**
    * Differential flows.
    * Choice of method, event-plane or two-particle correlation.
    * ATLAS-style unfolding.
    * Fits to flow coefficient distributions.

* **Data managament:**
Data will be stored in a database via an [ORM](https://en.wikipedia.org/wiki/Object-relational_mapping), probably [Django](https://www.djangoproject.com).

* **Other common calculations:**
pT spectra.

* **Plotting:**
Shortcuts for making common plots with matplotlib.



## Coding style

Every effort is made to keep code clean, consistent, and thoroughly commented.

* The [Python style guide](http://www.python.org/dev/peps/pep-0008) is followed whenever possible.
* All public functions and class methods have [docstrings](http://www.python.org/dev/peps/pep-0257).
* Private class attributes and methods are prefixed with an underscore.  This makes no difference to Python, it's just a human-readable flag that the
object is only meant to be used internally.
*  Python's [fileinput](http://docs.python.org/3/library/fileinput.html) module is used for all data input.  It provides a standardized method to iterate over
all input lines, from files or stdin, and handle compressed files transparently.
