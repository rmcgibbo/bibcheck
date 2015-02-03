import requests
import codecs
from bibcheck.latexencoding import register as register_latexcodec
register_latexcodec()


def retreive_doi(search):
    r = requests.get('http://search.crossref.org/dois',
        params={'q': search, 'rows':1})
    doi = r.json()[0]['doi']
    return doi

def retreive_bibtex(doi):
    r = requests.get('http://api.crossref.org/works/' + doi + '/transform/application/x-bibtex')
    return codecs.encode(r.content.decode('utf-8'), 'latex')


# print(retreive_bibtex('10.1021/ct4003477'))
