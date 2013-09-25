# EbE analysis

Tools for analyzing event-by-event heavy-ion collision simulation data.



## Design

* **Unix-style tools:**
Executables behave like Unix stream processors (grep, sed, etc.), i.e. they read from stdin or files on disk and output to stdout.

* **Modular worker classes:**
The real work occurs in the classes located in `lib/`.  This makes it trivial to reuse functionality.

* **Lightweight particle format:**
In "standard" format, each particle is represented by four quantities:  Monte Carlo ID, pT, phi, eta.  This is roughly 75% smaller on disk than UrQMD files.

* **Minimal dependencies:**
Python 3 and NumPy; SciPy for statistical functions; Matplotlib for plotting.



## Usage

Executables are located in the root directory and prefixed with `ebe-`.  It's easiest if the directory is appended to the shell path.  All executables have
built-in usage information accessible via the `-h/--help` command-line switch.

### Reading events

Two event formats are currently supported:  UrQMD file 13 and the standard format ID,pT,phi,eta.  All event-reading executables can handle either format, but
reading from UrQMD is somewhat slower (see [optimization](#optimization)).

Scripts will attempt to automatically determine format via filename.  This is very simple:  if '.f13' is in the filename, it is assumed to be UrQMD, else
standard.  Note that if reading from stdin, there is no filename, and scripts will assume standard format.  This can always be overridden with the `-f/--format`
flag; acceptable choices are 'auto' (default), 'urqmd', or 'std'.

`ebe-read` parses either format and outputs standard format.  This is useful for

* saving disk space,
* speeding up subsequent reads, and/or
* [filtering particles](#filtering-particles).

Suppose `0.f13`, `1.f13` are UrQMD files, then the following are equivalent

    ebe-read 0.f13 1.f13
    cat 0.f13 1.f13 | ebe-read -f urqmd

If several events are in one file:

    ebe-read events.f13
    ebe-read -f urqmd < events.f13

Read all files in the cwd and store in standard form:

    ebe-read *.f13 > events.dat

### Calculating flow coefficients

`ebe-flows` reads events and calculates flows event-by-event:

    ebe-read *.f13 | ebe-flows
    ebe-flows events.dat

The default range of v\_n is 2-6 and is set by `-n/--vn`, e.g. `ebe-flows -n 2 6`.

Flows are output in the format

    v_min ... v_max

With the `-v/--vectors` flag, flow vector components are output:

    v_min_x v_min_y ... v_max_x v_max_y

Use the `--avg` flag for average flows over all events.

Use `-d/--diff [width]` for average differential flows in pT-bins of the specified width.  In this case, the output format is

    pT_mid N_particles flows

where `pT_mid` is the middle pT value of the bin, `N_particles` is the number of particles in that bin, and `flows` are the calculated flows for the bin, either
magnitudes or vectors as requested.

### Calculating multiplicities

`ebe-multiplicity` reads events and calculates multiplicities event-by-event.

### Fitting

`ebe-fit` fits flow distributions to the SciPy generalized gamma distribution and multiplicity distributions to Gaussians (i.e. calculate mean and standard
deviation).  Basic usage is

    ebe-fit {gengamma,norm} [files ...]

where the first argument specifies the type of fit.

### Filtering particles

All event-reading scripts can filter particles by species, transverse momentum, and rapidity.  Full details are provided by the `-h/--help` flag; some examples
follow:

Read a UrQMD file and output only pions:

    ebe-read --ID 211,-211,111 events.f13 > pions.dat

Calculate flows from UrQMD with ATLAS conditions:

    ebe-flows --charged --pTmin 0.5 --etamax 2.5 *.f13 > flows.dat
    ebe-flows --atlas *.f13 > flows.dat

Calculate mid-rapidity charged-particle yields from standard format:

    ebe-multiplicity --charged --etamax 0.5 events.dat
    ebe-multiplicity --mid events.dat



## Optimization

All benchmarks were performed on an Intel i5-2500 (four cores at 3.3 GHz).  Test files were stored in tmpfs to eliminate disk IO effects.  Reading large
files from e.g. NFS will probably be slower.

### Event reading speed

Reading UrQMD is considerably slower than standard format due to the additional processing required.  For a test event of 8571 particles,
reading in UrQMD format took 66.3 ms; reading in standard format took only 29.6 ms.

Note that these are the reading times only; printing adds somewhat more (the precise amount depends on if the output is redirected).

### Python interpreter overhead

It takes a moment for the Python interpreter to start up and import all required modules:  "reading" a blank event (`ebe-read <<< ''`) takes roughly 90 ms.
Reading the 8571 particle test event in standard format and redirecting the output to /dev/null takes roughly 175 ms, 10 events takes 985 ms, 1000 events takes
92 seconds.

### Compression

All scripts can read compressed files (gzip,bz2,xz) transparently.  For example,

    ebe-read events.f13.gz

works fine.  However, Python's decompression is somewhat slower than the C versions, so it's generally better to use e.g.

    zcat events.f13.gz | ebe-read -f urqmd

The 8571-particle test event takes 205 ms the first way and 175 ms the second way (i.e. zcat has negligible overhead).

xz typically offers the best compression, but gzip is the fastest.

### Parallelization

EbE-analysis does not have native parallelization, and I have no plans to implement it, for I believe it would be beyond the scope of the project and the Unix
philosophy (is there a parallel grep?).  However, the wonderful [GNU Parallel](https://www.gnu.org/software/parallel) provides painless and effective parallelization of shell loops.

Suppose I have 40 files, `0-39.f13`, which I want to process. On my quad-core machine, I should split the 40 files into four groups, start four instances of the
executable, store the output in temporary files, then combine and clear the temporaries:

    ebe-read [0-9].f13 > tmp/0-9.dat &
    ebe-read 1[0-9].f13 > tmp/10-19.dat &
    ebe-read 2[0-9].f13 > tmp/20-29.dat &
    ebe-read 3[0-9].f13 > tmp/30-39.dat &
    cat tmp/*.dat > all.dat
    rm -r tmp

This works, but would be annoying to do repeatedly.  It could be semi-automated with a script, but that would likely be inflexible and
error-prone.

The exact same thing can be accomplished with

    parallel -Xk ebe-read ::: *.f13 > all.dat

The reader is encouraged to peruse the Parallel [man page](https://www.gnu.org/software/parallel/man.html), but to summarize:

* `:::` indicates the list of arguments.
* `-X` splits the arguments into approximately equal groups for each thread, e.g. on a quad-core machine the 40 file names are split into 4 groups of 10.  The
number of threads is autodetected and may be overridden.  It is easy to see what is happening via e.g. `parallel -X echo ::: *.f13`.
* `-k` ensures that the output is in the same order as if the commands had been run sequentially.

For benchmarking, I have a directory with 1000 UrQMD files, each with about 8000-10000 particles.  This is actual shell output:

    $ time ebe-read *.f13 > sequential
    ebe-read *.f13 > sequential  129.75s user 1.29s system 99% cpu 2:11.50 total

    $ time parallel -Xk ebe-read ::: *.f13 > parallel
    parallel -Xk ebe-read ::: *.f13 > parallel  138.77s user 2.07s system 333% cpu 42.273 total

    $ sha1sum sequential parallel
    372afe1a72cf80828a21abe8c6bdfa476782019f  sequential
    372afe1a72cf80828a21abe8c6bdfa476782019f  parallel

About 3.1 times faster, and the output is identical.



## To do

* Flows: two-particle correlation method, ATLAS-style unfolding.
* Plotting shortcuts.
* Support for UrQMD 3.3 format.
