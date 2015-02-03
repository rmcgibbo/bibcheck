from __future__ import print_function, absolute_import
import os
import sys
from argparse import ArgumentParser
PY2 = sys.version_info[0] == 2
if PY2:
    from codecs import open

from . import bib
from . import schemas


def parse_cmd_line():
    def bibtexfilename(fn):
        if not fn.endswith('.bib'):
            raise ValueError('bibtex filename must end in .bib')
        return fn

    argparser = ArgumentParser(description="""
    Validator for bibtex files
    """)
    argparser.add_argument('bibtex', type=bibtexfilename)
    argparser.add_argument('-v', '--verbose', action='store_true')
    argparser.add_argument('--schema', default='ACS', help='The schema specifies which bibtex fields are required for a particular journal. Default="ACS"', choices=['ACS'])

    args = argparser.parse_args()
    # print args
    return args

def main():
    args = parse_cmd_line()
    with open(args.bibtex, 'r', encoding='utf-8') as f:
        lines = os.linesep.join(l.strip() for l in f)

    bibobject = bib.Bibparser(lines, verbose=args.verbose)
    bibobject.parse()

    schema = getattr(schemas, args.schema)
    bibobject.validate(schema)
