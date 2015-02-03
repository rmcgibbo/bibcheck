"""
Copyright (C) 2011 by Panagiotis Tigkas <ptigas@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
from __future__ import print_function, absolute_import
import os
import re
import sys
import json
from collections import OrderedDict
from pprint import pprint
from six import iteritems
PY3 = sys.version_info[0] == 3

if PY3:
    def iteritems(d, **kw):
        return iter(d.items(**kw))
else:
    def iteritems(d, **kw):
        return iter(d.iteritems(**kw))

from . import abbrevs

def clear_comments(data):
    """Return the bibtex content without comments"""
    res = re.sub(r"(%.*\n)", '', data)
    res = re.sub(r"(comment [^\n]*\n)", '', res)
    return res

def log( f ):
    return f

def warn(msg):
    print('Warning: {}'.format(msg))

class Bibparser() :
    """Main class for Bibtex parsing"""

    def tokenize(self) :
        """Returns a token iterator"""
        for item in self.token_re.finditer(self.data):
            i = item.group(0)
            if self.white.match(i) :
                if self.nl.match(i) :
                    self.line += 1
                continue
            else :
                yield i

    def __init__(self, data, verbose=False):
        self.data = data
        self.token = None
        self.token_type = None
        self._next_token = self.tokenize().__next__
        self.hashtable = {}
        self.mode = None
        self.records = OrderedDict()
        self.line = 1
        self.verbose = verbose

        # compile some regexes
        self.white = re.compile(r"[\n|\s]+")
        self.nl = re.compile(r"[\n]")
        self.token_re = re.compile(r"([^\s\"#'(){}@,=]+|\n|@|\"|{|}|=|,)")

    def parse(self) :
        """Parses self.data and stores the parsed bibtex to self.rec"""
        while True :
            try :
                self.next_token()
                while self.database() :
                    pass
            except StopIteration :
                break

    def next_token(self):
        """Returns next token"""
        self.token = self._next_token()
        if self.verbose:
            print((self.line, self.token))

    @log
    def database(self) :
        """Database"""
        if self.token == '@' :
            self.next_token()
            self.entry()

    @log
    def entry(self) :
        """Entry"""
        if self.token.lower() == 'string' :
            self.mode = 'string'
            self.string()
            self.mode = None
        else :
            self.mode = 'record'
            self.record()
            self.mode = None

    @log
    def string(self) :
        """String"""
        if self.token.lower() == "string" :
            self.next_token()
            if self.token == "{" :
                self.next_token()
                self.field()
                if self.token == "}" :
                    pass
                else:
                    raise NameError("} missing: %s" % self.token)

    @log
    def field(self) :
        """Field"""
        name = self.name()
        if self.token == '=' :
            self.next_token()
            value = self.value()
            if self.mode == 'string' :
                self.hashtable[name] = value
            return (name, value)

    @log
    def value(self) :
        """Value"""
        value = ""
        val = []

        while True :
            if self.token == '"' :
                while True:
                    self.next_token()
                    if self.token == '"' :
                        break
                    else :
                        val.append(self.token)
                if self.token == '"' :
                    self.next_token()
                else :
                    raise NameError("\" missing")
            elif self.token == '{' :
                brac_counter = 0
                while True:
                    self.next_token()
                    if self.token == '{' :
                        brac_counter += 1
                    if self.token == '}' :
                        brac_counter -= 1
                    if brac_counter < 0 :
                        break
                    else :
                        val.append(self.token)
                if self.token == '}' :
                    self.next_token()
                else :
                    raise NameError("} missing")
            elif self.token != "=" and re.match(r"\w|#|,", self.token) :
                value = self.query_hashtable(self.token)
                val.append(value)
                while True:
                    self.next_token()
                    # if token is in hashtable then replace
                    value = self.query_hashtable(self.token)
                    if re.match(r"[^\w#]|,|}|{", self.token) : #self.token == '' :
                        break
                    else :
                        val.append(value)

            elif self.token.isdigit() :
                value = self.token
                self.next_token()
            else :
                if self.token in self.hashtable :
                    value = self.hashtable[ self.token ]
                else :
                    value = self.token
                self.next_token()

            if re.match(r"}|,",self.token ) :
                break

        value = ' '.join(val)
        return value

    def query_hashtable( self, s ) :
        if s in self.hashtable :
            return self.hashtable[ self.token ]
        else :
            return s

    @log
    def name(self) :
        """Returns parsed Name"""
        name = self.token
        self.next_token()
        return name

    @log
    def key(self) :
        """Returns parsed Key"""
        key = self.token
        self.next_token()
        return key

    @log
    def record(self) :
        """Record"""
        if self.token not in ['comment', 'string', 'preamble'] :
            record_type = self.token
            self.next_token()
            if self.token == '{' :
                self.next_token()
                key = self.key()
                self.records[ key ] = {}
                self.records[ key ]['type'] = record_type.lower()
                self.records[ key ]['id'] = key
                if self.token == ',' :
                    while True:
                        self.next_token()
                        field = self.field()
                        if field :
                            k = field[0]
                            val = field[1]

                            if k == 'author' :
                                val = self.parse_authors(val)

                            if k == 'year' :
                                val = {'literal':val}
                                k = 'issued'

                            if k == 'pages' :
                                val = val.replace('--', '-')
                                k = 'page'

                            if k == 'title' :
                                #   Preserve capitalization, as described in http://tex.stackexchange.com/questions/7288/preserving-capitalization-in-bibtex-titles
                                #   This will likely choke on nested curly-brackets, but that doesn't seem like an ordinary practice.
                                def capitalize(s):
                                    return s.group(1) + s.group(2).upper()
                                while val.find('{') > -1:
                                    caps = (val.find('{'), val.find('}'))
                                    val = val.replace(val[caps[0]:caps[1]+1], re.sub("(^|\s)(\S)", capitalize, val[caps[0]+1:caps[1]]).strip())

                            self.records[ key ][k] = val
                        if self.token != ',' :
                            break
                    if self.token == '}' :
                        pass
                    elif self.token.startswith('%'):
                        pass
                    else :
                        # assume entity ended
                        if self.token == '@' :
                            pass
                        else:
                            raise NameError("@ missing %s" % self.token)

    def parse_authors(self, authors):
        res = []
        authors = authors.split(' and ')
        for author in authors:
            _author = author.split(',')
            family = _author[0].strip().rstrip()
            rec = {'family': family}
            try :
                given = _author[1].strip().rstrip()
                rec['given'] = given
            except IndexError:
                pass
            res.append(rec)
        return res

    # def json(self) :
    #     """Returns json formated records"""
    #     return json.dumps({'items':self.records.values())})
    #
    def rename_ids(self):
        newrecords = OrderedDict()
        counter = 0
        for key, value in iteritems(self.records):
            newkey = value['author'][0]['family'].split()[-1] + value['issued']['literal'] + value['title'].split()[0]
            newkey = newkey.lower()
            value['id'] = newkey

            newrecords[newkey] = value

        self.records = newrecords

    def to_bibtex(self):
        alllines = []
        for key, value in iteritems(self.records):
            type = value.pop('type')
            id = value.pop('id')
            lines = ['@%s{%s' % (type, id)]
            for k, v in iteritems(value):
                if k == 'author':
                    q = ' and '.join([a.get('given', '') + ' '+ a['family'] for a in v])
                    q = q.strip().replace('  ', ' ')
                    q = q.replace(' { ', '{').replace(' } ', '}')
                    lines.append('author = {%s}' % q)
                elif k == 'issued':
                    lines.append('year = {%s}' % v['literal'])
                else:
                    lines.append('%s = {%s}' % (k, v))

            record = ',\n'.join(lines) + '\n}'
            alllines.append(record)
        return '\n'.join(alllines)

    def validate(self, schema):
        warner = Warner()
        n_validated_entries = 0
        journal_validator = abbrevs.Validator()


        for key, value in iteritems(self.records):
            type = value['type'].lower()
            if type not in schema:
                warner.warn('Schema does not have an entry for type={}'.format(type))
            else:
                required_items = schema[type].keys()
                missing_items = set(required_items) - set([e.lower() for e in value.keys()])
                # the line that this entry is on
                line = next((i for i, l in enumerate(self.data.split(os.linesep)) if key in l))
                for item in missing_items:
                    print('\033[91mERROR: "{}" is missing field "{}" on line {}\033[0m'.format(key, item, line))
                # if len(missing_items) > 0:
                    # print value

            if 'journal' in value:
                recommendation = journal_validator.validate(value['journal'])
                if recommendation is not None:
                    msg = '\033[93mWARNING: Journal in {} (line {}), "{}" was not correct. Consider "{}"\033[0m'
                    print(msg.format(key, line, value['journal'], recommendation))
                    print()


            n_validated_entries += 1

        print('Entries validated:', n_validated_entries)


class Warner(object):
    def __init__(self):
        self._sent = set()

    def warn(self, msg):
        if msg not in self._sent:
            print('Warning: {}'.format(msg))
            self._sent.add(msg)
