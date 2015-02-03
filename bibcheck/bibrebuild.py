from __future__ import print_function, absolute_import
import os
import sys
import shutil
from argparse import ArgumentParser
PY2 = sys.version_info[0] == 2
if PY2:
    from codecs import open
    def iteritems(d, **kw):
        return iter(d.iteritems(**kw))
else:
    def iteritems(d, **kw):
        return iter(d.items(**kw))

from bibcheck import bib
from bibcheck import schemas
from bibcheck.crossref import retreive_bibtex, retreive_doi


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

    for key, value in iteritems(bibobject.records):
        if 'doi' in value:
            out = retreive_bibtex(value['doi'])
        else:
            try:
                doi = retreive_doi(value['title'] + ' ' + value['journal'])
                out = retreive_bibtex(doi)
            except:
                print("ERROR")
                pass

        bp = bib.Bibparser(out)
        bp.parse()
        bp.rename_ids()
        print(bp.to_bibtex())
        print()

if __name__ == '__main__':
    main()
