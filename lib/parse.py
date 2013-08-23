"""
Helpers for EbE argument parsing.

The module defines EbEParser: an argparse.ArgumentParser with a set of inherited
generic EbE arguments.  Any EbE script can use it easily via

>>> from lib.parse import EbEParser
>>> parser = EbEParser(...)

parser now behaves like a regular ArgumentParser.  EbEParser is tailored for use
with ebeinput.events_from_files, e.g.

>>> args = parser.parse_args()
>>> from lib.ebeinput import events_from_files
>>> events_from_files(**vars(args))
"""


from argparse import ArgumentParser
from functools import partial


# create a parent parser to hold generic arguments
# disable help, else its children will have redundant help messages
parent_parser = ArgumentParser(add_help=False)


# filenames are the only positional args
parent_parser.add_argument('files', nargs='*', 
    help="Files to read.  Omit or use '-' to read from stdin.")

# optional arg: file format
parent_parser.add_argument('-f', '--format', dest='inputformat',
    choices=['auto','std','urqmd'], default='auto', 
    help='Input format, default:  %(default)s.')


# create an argument group to hold particle filtering options
# these options will be listed separately from the rest in help
filter_parser = parent_parser.add_argument_group('particle filtering arguments')


# IDs and charged should not be specified simultaneously
ID_group = filter_parser.add_mutually_exclusive_group()

ID_group.add_argument('-i', '--ID', type=int, nargs='+',
    help='Particle IDs.')

ID_group.add_argument('-c', '--charged', action='store_true',
    help='All charged particles.')


filter_parser.add_argument('-p', '--pTmin', type=float, help='pT minimum.')
filter_parser.add_argument('-q', '--pTmax', type=float, help='pT maximum.')

filter_parser.add_argument('-g', '--etamin', type=float,
    help='eta minimum; if no etamax, interpreted as etamin < |eta|.')
filter_parser.add_argument('-e', '--etamax', type=float,
    help='eta maximum; if no etamin, equivalent to |eta| < etamax.')


"""
The EbEParser class.  

Just a regular ArgumentParser but with the parents kwarg preset.
"""

EbEParser = partial(ArgumentParser, parents=[parent_parser])
