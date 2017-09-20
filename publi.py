#!/usr/bin/env ipython3 --

"""A program to build, update, export publications

..moduleauthor:: Rasmus Diederichsen <rdiederichse@uos.de>
"""
import argparse
import copy
from itertools import combinations
from pickle import dump, load
from pathlib import Path
from pybtex.database import BibliographyData
from pylatexenc.latex2text import LatexNodes2Text
import pybtex.database
import string
from unidecode import unidecode
from re import split
import textwrap

private_fields = set(['publipy_pdfurl', 'publipy_biburl', 'mytype', 'key',
                      'url_home', 'publipy_abstracturl'])
stopwords = set(['the', 'a', 'of', 'in', 'der', 'die', 'das', 'ein', 'eine'])


def make_plain(text):
    return unidecode(LatexNodes2Text().latex_to_text(text))


def generate_swe_key(entry):
    if 'author' in entry.persons:
        person = '-'.join(entry.persons['author'][0].last_names)
    elif 'editor' in entry.persons:
        person = '-'.join(entry.persons['editor'][0].last_names)
    else:
        person = ''
    title_field = 'title' if 'title' in entry.fields else 'booktitle'
    try:
        title_word = next(make_plain(w)
                          for w in split(r'[\s:.,]', entry.fields[title_field])
                          if make_plain(w).lower() not in stopwords
                          and w not in string.punctuation)
    except StopIteration:
        title_word = ''
    year = entry.fields['year'] if 'year' in entry.fields else ''

    person = make_plain(person).lower()
    title_word = title_word.lower()
    return ':'.join([person, title_word, year])


def generate_key_bibtool(entry):
    """ Generate a key like bibtool would create with the following options
            key.base=lower
            key.format=short
    """
    if 'author' in entry.persons:
        authors = entry.persons['author']
    elif 'editor' in entry.persons:
        authors = entry.persons['editor']
    else:
        raise ValueError('No author or editor present')
    persons = '.'.join(map(lambda p: '-'.join(p.last_names), authors))
    if 'title' in entry.fields:
        title = entry.fields['title']
    elif 'booktitle' in entry.fields:
        title = entry.fields['booktitle']
    else:
        raise ValueError('No title or booktitle present')
    return (persons + ':' + title.split()[0]).lower()


def generate_suffix(key, keyset, current_suffix=''):
    for suffix in range(97, 123):
        if key + '.' + current_suffix + chr(suffix) not in keyset:
            return current_suffix + chr(suffix)
    return generate_suffix(key, keyset, current_suffix + 'a')


def disambiguate(key, keyset):
    """Disambiguate key over set of keys by successively appending more
    alphanumeric numbers."""
    if key not in keyset:
        return key
    return key + ':' + generate_suffix(key, keyset)


class PublicationDatabase(object):
    """Class to hold information about publication lists"""

    @classmethod
    def default_comparator(cls, item1, item2):
        """Default comparator for bibliograpyh items.This function will first
        compare the keys and then check whether both entries have a title field
        and if so, check whether their values are
        equal.

        :param cls: Class object
        :type cls: class
        :param item1: First bibliography item
        :type item1: tuple
        :param item2: Second bibliography item
        :type item2: tuple
        :returns: bool -- whether the two are duplicates or not
        """
        key1, entry1 = item1
        key2, entry2 = item2
        if key1 == key2:
            return True
        else:
            fields1, fields2 = (entry1.fields, entry2.fields)
            if 'title' in fields1.keys() and 'title' in fields2.keys():
                return fields1['title'] == fields2['title']
            else:
                return False

    def __init__(self, database_file=None, prefix=None):
        """Create a database by reading all the .bib files listed in a file.

        :param database_file: Json file listing members and associated file
        locations of bibfiles
        :type databses_file: str
        :param prefix: Folder prefix for saving/loading individual bib files and
            pdfs
        :type prefix: str
        """
        if database_file:
            self.database_file = database_file
            self.prefix = Path(prefix) if prefix else Path(database_file).parent
            self.populate(database_file)

    def __delitem__(self, key):
        self.delete(key)

    def delete(self, key):
        """Remove item from bilbiography

        :param key: Bibliography key to delete
        :type key: str
        """
        for publications in self.publications.values():
            for k in publications.entries.keys():
                if k == key:
                    # dirty hack since CaseInsensitiveOrderedDict does not
                    # support deletion
                    del publications.entries.__dict__['_dict'][k]

        # clean up bib file and pdf
        bibfile = self.prefix / Path('bib') / Path('%s.bib' % key)
        if bibfile.exists():
            bibfile.unlink()

        # pdffile = self.prefix / Path('pdf') / Path('%s.pdf'
        #                                                                % key)
        # if pdffile.exists():
        #     pdffile.unlink()

    def save(self):
        """Serialize self to pickled file named 'db.pckl'"""
        with open('db.pckl', mode='wb') as f:
            dump(self.publications, f)

        # update the original database file
        if self.database_file:
            self.publications.to_file(self.database_file, bib_format='bibtex')
            bibdir = self.prefix / Path('bib')
            abstractdir = self.prefix / Path('abstracts')
            if not bibdir.exists():
                bibdir.mkdir()
            if not abstractdir.exists():
                abstractdir.mkdir()
            for key, item in self.publications.entries.items():
                # make copy without our secret fields
                item = copy.copy(item)
                item.fields = {k: v for k, v in item.fields.items()
                               if k not in private_fields}
                # write single bib entry
                bibfile = bibdir / Path(key + '.bib')
                BibliographyData({key: item}).to_file(str(bibfile),
                                                      bib_format='bibtex')
                # write abstract separately, if present. Format to 80 characters
                if 'abstract' in item.fields:
                    abstract_file = abstractdir / Path(key + '.txt')
                    abstract = item.fields['abstract']
                    with open(str(abstract_file),
                              mode='w', encoding='utf8') as f:
                        text = LatexNodes2Text().latex_to_text(abstract)
                        f.write('\n'.join(textwrap.wrap(text, width=80)))

    def load(self):
        """Deserialize self from pickled file named 'db.pckl'."""
        with open('db.pckl', mode='rb') as f:
            self.publications = load(f)

    def populate(self, database_file):
        """Collect all bibdata from all files into one big-ass database.

        :param database_file: File listing members and locations of bibfiles
        :type database_file: str
        """

        self.publications = BibliographyData()
        publications = read_bibfile(database_file).entries
        for item in publications.values():
            key = generate_swe_key(item)
            item.fields['key'] = key
            if 'publipy_biburl' not in item.fields:
                item.fields['publipy_biburl'] = str(self.prefix / Path('bib') /
                                                    Path(key + '.bib'))
            if 'publipy_pdfurl' not in item.fields:
                item.fields['publipy_pdfurl'] = str(self.prefix / Path('pdf') /
                                                    Path(key + '.pdf'))
            if 'abstract' in item.fields:
                item.fields['publipy_abstracturl'] = str(self.prefix /
                                                         Path('abstracts') /
                                                         Path(key + '.txt'))

            self.add_entry(key, item)

    def find_duplicates(self, comparator=None):
        """Find suspected duplicates.
        :param comparator: binary function to determine whether two bib items
        (of type (:class: `str`, :class: `pybtex.Entry`))
        """
        if not comparator:
            comparator = PublicationDatabase.default_comparator
        suspects = []
        for publications in self.publications:
            # it seems that OrderedCaseInsensitiveDict, which inherits from
            # MutableMapping, does not provide an items() iterator, so we need
            # to form tuples manually
            combos = combinations([(key, publications.entries[key])
                                   for key in publications.entries], 2)
            for (item1, item2) in combos:
                if comparator(item1, item2):
                    suspects.append((item1, item2))
        return suspects

    def add_entry(self, key, entry):
        if not isinstance(entry, pybtex.database.Entry):
            raise ValueError('Expected type pybtex.database.Entry, got %' %
                             type(entry))
        else:
            if key in self.publications.entries:
                key = disambiguate(key, self.publications.entries.keys())
            self.publications.entries[key] = entry

    def add_bibdata(self, entries):
        if isinstance(entries, str):
            bibdata = pybtex.database.parse_string(entries, bib_format='bibtex')
        else:
            bibdata = entries  # Assume it's BibliographyData
        for v in bibdata.entries.values():
            key = disambiguate(generate_key_bibtool(v),
                               self.publications.entries.keys())
            print('Entry added with key key: %s' % key)
            self.add_entry(key, v)

    def iter_entries(self, predicate=None):
        predicate = predicate or (lambda x: True)
        for k, entry in self.publications.entries.items():
            if predicate(entry):
                yield (k, entry)

    def publications_for_year(self, min_year, max_year):
        if max_year <= min_year:
            raise ValueError("min_year must be smaller than max_year")

        def f(entry):
            for field_name, value in entry.fields:
                if field_name == 'year' and min_year <= int(value) <= max_year:
                    return True
            return False

        return self.iter_entries(predicate=f)

    def publications_for_type(self, type):
        def f(entry):
            return entry.type == type
        return self.iter_entries(predicate=f)

    def publications_for_member(self, member, fmt='bib'):
        raise ValueError('Not implemented')
        # if member not in self.publications:
        #     raise ValueError("Unknown group member.")
        # return self.publications['member']

    def build_publication_map(self, pdf_folder):
        from pdf_util import pdf_for_pub
        return {
            key: pdf_for_pub(entry, pdf_folder)
            for key, entry in self.iter_entries()
        }


def build(args):
    """Build a :class: `PublicationDatabase` from the arguments passed.

    :param args: :class: `Namespace` object obtained via :class:
        argparse.ArgumentParser's :link: `argparse.ArgumentParser.parse_args`
        method.
    :type args: argparse.Namespace
    :returns: database with all publications
    :rtype: PublicationDatabase

    """
    pubdata = PublicationDatabase(args.database)
    # duplicates = pubdata.find_duplicates()
    pubdata.save()
    # print("Suspected duplicates: ")
    # for item1, item2 in duplicates:
    #     print("\t{} == {}".format(item1[0], item2[0]))
    # for key, entry in pubdata.iter_entries():
    #     print(pdf_for_pub(entry, args.pdf_loc))
    # return pubdata


def add(args):
    pubdata = PublicationDatabase()
    pubdata.load()
    pubdata.add_bibdata(args.entries)
    pubdata.save()


def read_bibfile(filename):
    """Read a bibliography file and add a key field"""
    with open(filename) as f:
        db = pybtex.database.parse_file(f, 'bibtex')
        return db


def check_validity(entry):
    # TODO: Check if entry is valid by trying to render it
    pass


def render(args):
    db = PublicationDatabase()
    db.load()
    known_fmts = ['bib', 'html', 'latex']
    # eval won't be run until function is actually called
    predicate = lambda entry: eval(args.expr)
    try:
        publications = BibliographyData({k: v for k, v in
                                            db.iter_entries(predicate=predicate)})
    except SyntaxError:
        raise ValueError('\'%s\' is invalid syntax.' % args.expr)
    fmt = args.fmt
    if fmt == 'bib':
        result = publications.to_string(bib_format='bibtex')
    elif fmt == 'html':
        result = pybtex.format_from_string(
            publications.to_string(bib_format='bibtex'),
            'gerunsrtwithlinks',
            citations=publications.entries.keys(),
            bib_format='bibtex',
            bib_encoding=None,
            output_backend='html',
            output_encoding='utf8',
            moin_crossrefs=9999
        )
    elif fmt == 'latex':
        pass
    else:
        raise ValueError('Unknown format \'%s\' given. Known formats are ' +
                         ','.join(["{}"] * len(known_fmts)), fmt, *known_fmts)
    print(result)


def render_to_latex(bibdata, template):
    pass


def render_to_html(bibdata):
    pass


def main():
    """Process user commands."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subparser_name')

    ############################################################################
    #                             build subcommand                             #
    ############################################################################
    build_parser = subparsers.add_parser('build', help='Build a database')
    build_parser.add_argument('-d', '--database', required=True, type=str,
                              help=('Path to .bib file with all entries'))
    # build_parser.add_argument('-p', '--pdfs', required=True, type=str,
    #                           help='Path to pdf folder.', dest='pdf_loc')
    build_parser.set_defaults(func=build)

    ############################################################################
    #                             add subcommand                               #
    ############################################################################
    add_parser = subparsers.add_parser('add',
                                       help='Add something to the database')
    add_parser.add_argument('-e', '--entries', required=False, type=str,
                            help='bibtex entry to add')
    add_parser.add_argument('-f', '--file', required=False, type=str,
                            help='Bibfile to add to the database')
    add_parser.set_defaults(func=add)
    # TODO: Fuzzy author guessing

    ############################################################################
    #                             list subcommand                              #
    ############################################################################
    list_parser = subparsers.add_parser('list', help='List entries')
    list_parser.add_argument('-f', '--format', required=False, type=str,
                             default='bib', help='Format to output', dest='fmt',
                             choices=['bib', 'html', 'pdf'])
    list_parser.add_argument('-e', '--expr', required=False, type=str,
                             default='True',
                             help='Filter with python expression.'
                             'A variable \'entry\' denotes the'
                             'entry to consider', dest='expr')
    list_parser.set_defaults(func=render)

    args = parser.parse_args()
    if args.subparser_name:
        # dispatch subparser handler
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
