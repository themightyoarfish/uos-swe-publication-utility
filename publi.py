#!/usr/bin/env ipython3 --

"""A program to build, update, export publications

..moduleauthor:: Rasmus Diederichsen <rdiederichse@uos.de>
"""
import argparse
import shutil
import copy
from filters import get_conjunction_filter, get_person_filter, get_mytype_filter
from pickle import dump, load
from itertools import combinations
from difflib import SequenceMatcher
from pathlib import Path
from pybtex.database import BibliographyData, Entry
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


def generate_key_swe(entry):
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

    year = entry.fields['year'][-2:] if 'year' in entry.fields else ''

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
            if 'title' in entry1.fields:
                title1 = entry1.fields['title']
            elif 'booktitle' in entry1.fields:
                title1 = entry1.fields['booktitle']
            else:
                raise ValueError('Entry has neither title nor booktitle')
            if 'title' in entry2.fields:
                title2 = entry2.fields['title']
            elif 'booktitle' in entry2.fields:
                title2 = entry2.fields['booktitle']
            else:
                raise ValueError('Entry has neither title nor booktitle')

            similarity = SequenceMatcher(None, title1.split(),
                                         title2.split(),
                                         autojunk=False).ratio()
            return similarity > 0.8

    def __init__(self, database_file=None, pdf_dir=None, prefix=None):
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
            self.populate(database_file, pdf_dir)

    def __delitem__(self, key):
        self.delete(key)

    def delete(self, key):
        """Remove item from bilbiography

        :param key: Bibliography key to delete
        :type key: str
        """
        for k in self.publications.entries.keys():
            if k == key:
                # dirty hack since CaseInsensitiveOrderedDict does not
                # support deletion
                del self.publications.entries.__dict__['_dict'][k]

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
            self.publications.to_file(self.database_file,
                                      bib_format='custombibtex')
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
                                                      bib_format='custombibtex')
                # write abstract separately, if present. Format to 80 characters
                if 'abstract' in item.fields:
                    abstract_file = abstractdir / Path(key + '.txt')
                    abstract = item.fields['abstract']
                    with open(str(abstract_file),
                              mode='w', encoding='utf8') as f:
                        text = make_plain(abstract)
                        f.write('\n'.join(textwrap.wrap(text, width=80)))

    def load(self):
        """Deserialize self from pickled file named 'db.pckl'."""
        with open('db.pckl', mode='rb') as f:
            self.publications = load(f)

    def populate(self, database_file, pdf_dir):
        """Collect all bibdata from all files into one big-ass database.

        :param database_file: File listing members and locations of bibfiles
        :type database_file: str
        """

        self.publications = BibliographyData()
        publications = read_bibfile(database_file).entries

        # ensure the pdf directory exists
        if pdf_dir and not (self.prefix / Path('pdf')).exists():
            (self.prefix / Path('pdf')).mkdir()

        for oldkey, item in publications.items():
            key = generate_key_swe(item)
            if 'publipy_biburl' not in item.fields:
                item.fields['publipy_biburl'] = str(self.prefix / Path('bib') /
                                                    Path(key + '.bib'))
            if 'abstract' in item.fields:
                item.fields['publipy_abstracturl'] = str(self.prefix /
                                                         Path('abstracts') /
                                                         Path(key + '.txt'))

            if pdf_dir and 'publipy_pdfurl' not in item.fields:
                pdf_path_old = Path(pdf_dir) / Path(oldkey + '.pdf')
                if pdf_path_old.exists() and pdf_path_old.is_file():
                    pdf_path_new = self.prefix / Path('pdf') / Path(key +
                                                                    '.pdf')
                    shutil.copy(str(pdf_path_old), str(pdf_path_new))
                    item.fields['publipy_pdfurl'] = str(pdf_path_new)

            self.add_entry(key, item)

    def find_duplicates(self, comparator=None):
        """Find suspected duplicates.
        :param comparator: binary function to determine whether two bib items
        (of type (:class: `str`, :class: `pybtex.Entry`))
        """
        if not comparator:
            comparator = PublicationDatabase.default_comparator
        suspects = []
        # it seems that OrderedCaseInsensitiveDict, which inherits from
        # MutableMapping, does not provide an items() iterator, so we need
        # to form tuples manually
        combos = combinations([(key, self.publications.entries[key])
                               for key in self.publications.entries], 2)
        for (item1, item2) in combos:
            if comparator(item1, item2):
                # return only the keys
                suspects.append((item1[0], item2[0]))
        return suspects

    def add_entry(self, key, entry):
        if not isinstance(entry, pybtex.database.Entry):
            raise ValueError('Expected type pybtex.database.Entry, got %' %
                             type(entry))
        else:
            if key in self.publications.entries:
                key = disambiguate(key, self.publications.entries.keys())
                entry.fields['key'] = key
            self.publications.entries[key] = entry

    def __getitem__(self, key):
        return self.publications.entries[key]

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


def build(args):
    """Build a :class: `PublicationDatabase` from the arguments passed.

    :param args: :class: `Namespace` object obtained via :class:
        argparse.ArgumentParser's :link: `argparse.ArgumentParser.parse_args`
        method.
    :type args: argparse.Namespace
    :returns: database with all publications
    :rtype: PublicationDatabase

    """
    pubdata = PublicationDatabase(args.database, args.pdf_loc)
    # duplicates = pubdata.find_duplicates()
    # print("Suspected duplicates: ")
    # for key1, key2 in duplicates:
    #     bib1 = BibliographyData({key1: pubdata[key1]})
    #     bib2 = BibliographyData({key2: pubdata[key2]})
    #     print("\t{} == {}".format(bib1.to_string(bib_format='bibtex'),
    #                               bib2.to_string(bib_format='bibtex')))
    #     delete = input('Delete this? (y/n) ')
    #     if delete.lower() in ['y', 'ye', 'yes', 'yo']:
    #         pubdata.delete(key1)
    pubdata.save()


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


def print_all_authors():
    db = PublicationDatabase()
    db.load()
    entries = db.publications.entries.values()

    def textify(p):
        return make_plain(' '.join(p.last_names))

    def get_persons(e):
        return e.persons.values()

    unique_persons = set(textify(p) for persons in map(get_persons, entries) for
                         role in persons for p in role)
    import pprint
    pprint.pprint(sorted(unique_persons))


def filtered_entries(database, args):
    BibData = BibliographyData  # shorter

    # slap onto this all constraints
    def filter(entry):
        return True

    predicate = filter
    if args.person:
        predicate = get_conjunction_filter(predicate,
                                           get_person_filter(args.person))
    if args.mytype:
        predicate = get_conjunction_filter(predicate,
                                           get_mytype_filter(args.mytype))
    if args.expr:
        def filter_expr(entry):
            # TODO: Don't fckn eval user input, dipshit
            try:
                return eval(args.expr)  # won't be evaluated before call
            except KeyError:
                print('Warning: KeyError')
                return False
        try:
            filter_expr(Entry(''))  # eval with dummy entry to force parsing
            predicate = get_conjunction_filter(predicate, filter_expr)
        except SyntaxError:
            print('\'%s\' is invalid syntax. Ignoring expression filter' %
                  args.expr)

    publications = BibData({k: v for k, v in
                            database.iter_entries(predicate=predicate)})
    return publications


def render(args):
    db = PublicationDatabase()
    db.load()
    known_fmts = ['bib', 'html', 'text', 'pdf']

    publications = filtered_entries(db, args)

    fmt = args.fmt
    if fmt == 'bib':
        result = publications.to_string(bib_format='bibtex')
    elif fmt == 'html':
        from plugin_data import plugin_data
        plugin_data['label_start'] = 0
        plugin_data['write_html_wrapper'] = args.complete_html
        result = pybtex.format_from_string(
            publications.to_string(bib_format='custombibtex'),
            'gerunsrtwithlinks',
            citations=publications.entries.keys(),
            bib_format='bibtex',
            bib_encoding=None,
            output_backend='customhtml',
            output_encoding='utf8'
        )
    elif fmt == 'tex':
        raise NotImplementedError()
    elif fmt == 'pdf':
        raise NotImplementedError()
    else:
        raise ValueError('Unknown format \'%s\' given. Known formats are ' +
                         ','.join(["{}"] * len(known_fmts)), fmt, *known_fmts)
    outfile = args.out
    if not outfile.endswith(fmt):
        outfile += '.%s' % fmt

    with open(outfile, mode='w', encoding='utf8') as f:
        f.write(result)


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
    build_parser.add_argument('-p', '--pdfs', required=False, default=None,
                              type=str, help='Path to pdf folder.',
                              dest='pdf_loc')
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
                             choices=['bib', 'html', 'tex', 'pdf'])
    list_parser.add_argument('-o', '--out', required=True, type=str,
                             default='bibliography', help='File to output to',
                             dest='out')
    list_parser.add_argument('-e', '--expr', required=False, type=str,
                             help='Filter with python expression. '
                             'A variable \'entry\' denotes the '
                             'entry to consider')
    list_parser.add_argument('-p', '--person', required=False, type=str,
                             help='Print only publications this person is '
                             'involved in (be it author or editor)')
    list_parser.add_argument('-t', '--mytype', required=False, type=str,
                             help='Print only publications that have '
                             'this mytype')
    list_parser.add_argument('-c', '--complete_html', required=False,
                             action='store_true', dest='complete_html',
                             help='Whether or not to produce valid HTML '
                             'or only the <dl> element to place inside another '
                             'document. Ignored in any format except html')

    list_parser.set_defaults(func=render)

    args = parser.parse_args()
    if args.subparser_name:
        # dispatch subparser handler
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
