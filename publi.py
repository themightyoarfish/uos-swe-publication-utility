#!/usr/bin/env python3

"""A program to build, update, export publications

..moduleauthor:: Rasmus Diederichsen <rdiederichse@uos.de>
"""
import argparse
import json
import sys
from itertools import combinations
from pickle import dump, load

import pybtex.database

DATABASES_FILE = "databases.json"


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

    def __init__(self, databases_file=None):
        """Create a database by reading all the .bib files listed in a file.

        :param databases_file: Json file listing members and associated file
        locations of bibfiles
        :type databses_file: str
        """
        if databases_file:
            self.databases_file = databases_file
            self.populate(databases_file)

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

    def save(self, to_file=False):
        """Serialize self to pickled file named 'db.pckl'"""
        if not to_file:
            with open('db.pckl', mode='wb') as f:
                dump(self.publications, f)
        else:
            with open(self.databases_file) as f:
                databases = json.load(f)
                authors = databases['bibfiles']
                for entry in authors:
                    author = entry['author']
                    path = entry['path']
                    if author in self.publications:
                        self.publications[author].to_file(path,
                                                          bib_format='bibtex')
                    else:
                        print(('Warning: "%s" not found in publications but'
                               'in databases' % author), file=sys.stderr)

    def load(self):
        """Deserialize self from pickled file named 'db.pckl'."""
        with open('db.pckl', mode='rb') as f:
            self.publications = load(f)

    def populate(self, databases_file):
        """Collect all bibdata from all files into one big-ass database.

        :param databases_file: File listing members and locations of bibfiles
        :type databases_file: str
        """

        with open(databases_file) as file:
            databases = json.load(file)
            # db has entries of (author: foo, path: bar), which we obtain by
            # asking the dict for its values (removing the keys) and turning
            # them into tuples so we can do (a,b) = tup on them in the dict
            # comprehension below. Why not just use d.values() in lambda?
            # Because the order is non-deterministic
            self.publications = {
                    member: read_bibfile(bibloc)
                    for (member, bibloc) in
                    map(lambda d: (d['author'], d['path']),
                        databases['bibfiles'])
            }
        keys = [key for bibdata in self.publications.values() for key in
                        bibdata.entries.keys()]
        self.keys = set(keys)

    def find_duplicates(self, comparator=None):
        """Find suspected duplicates.
        :param comparator: binary function to determine whether two bib items
        (of type (:class: `str`, :class: `pybtex.Entry`))
        """
        if not comparator:
            comparator = PublicationDatabase.default_comparator
        suspects = []
        for publications in self.publications.values():
            # it seems that OrderedCaseInsensitiveDict, which inherits from
            # MutableMapping, does not provide an items() iterator, so we need
            # to form tuples manually
            combos = combinations([(key, publications.entries[key])
                                   for key in publications.entries], 2)
            for (item1, item2) in combos:
                if comparator(item1, item2):
                    suspects.append((item1, item2))
        return suspects

    def add_entry(self, member, key, entry):
        if not isinstance(entry, pybtex.database.Entry):
            raise ValueError('Expected type pybtex.database.Entry, got %' %
                             type(entry))
        if member not in self.publications:
            self.publications[member] = pybtex.database.BibliographyData(
                {key: entry})
        else:
            if key in self.publications[member].entries:
                raise ValueError('Key already taken.')
            self.publications[member].entries[key] = entry

    def add_bibdata(self, member, entries):
        if isinstance(entries, str):
            bibdata = pybtex.database.parse_string(entries, bib_format='bibtex')
        for k, v in bibdata.entries.items():
            self.add_entry(member, k, v)

    def render(publications, fmt='bib'):
        known_fmts = ['bib', 'html', 'latex']
        if fmt not in known_fmts:
            raise ValueError(
                "Unknown format given. Known formats are {}, {}, {}", *fmt)

    def iter_entries(self, member=None):
        if not member:
            for member, pubs in self.publications.items():
                for k, entry in pubs.entries.items():
                    yield (k, entry)
        else:
            if member not in self.publications:
                raise ValueError("Unknown group member.")
                for k, entry in pubs.entries.items():
                    yield (k, entry)

    def filter_entries(self, fn=lambda e: True):
        return [entry for entry in self.iter_entries() if fn(entry)]

    def publications_for_year(self, min_year, max_year):
        if max_year <= min_year:
            raise ValueError("min_year must be smaller than max_year")

        def f(entry):
            for field_name, value in entry.fields:
                if field_name == 'year' and min_year <= int(value) <= max_year:
                    return True
            return False

        return self.filter_entries(fn=f)

    def publications_for_type(self, type):
        def f(entry):
            return entry.type == type
        return self.filter_entries(fn=f)

    def publications_for_member(self, member, fmt='bib'):
        if member not in self.publications:
            raise ValueError("Unknown group member.")
        return self.publications['member']

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
    pubdata = PublicationDatabase(args.databases)
    # duplicates = pubdata.find_duplicates()
    pubdata.save(to_file=True)
    # print("Suspected duplicates: ")
    # for item1, item2 in duplicates:
    #     print("\t{} == {}".format(item1[0], item2[0]))
    # for key, entry in pubdata.iter_entries():
    #     print(pdf_for_pub(entry, args.pdf_loc))
    # return pubdata


def add(args):
    pubdata = PublicationDatabase()
    pubdata.load()
    pubdata.add_bibdata(args.member, args.entries)
    pubdata.save()


def read_bibfile(filename):
    with open(filename) as f:
        return pybtex.database.parse_file(f, 'bibtex')


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
    build_parser.add_argument('-d', '--databases', required=True, type=str,
                              help=('json file with absolute paths'
                                    'to all relevant bibtex files'))
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
    add_parser.add_argument('-m', '--member', required=True, type=str,
                            help=('name of the group member to'
                                  'add the publication to'))
    add_parser.add_argument('-f', '--file', required=False, type=str,
                            help='Bibfile to add to the database')
    add_parser.set_defaults(func=add)
    # TODO: Fuzzy author guessing

    ############################################################################
    #                             list subcommand                              #
    ############################################################################
    list_parser = subparsers.add_parser('list', help='Build a database')
    list_parser.add_argument('-f', '--format', required=False, type=str,
                             default='bib',
                             help='Format to output', choices=['bib', 'html', 'pdf'])

    args = parser.parse_args()
    # not sure how to handle no subcommand given
    if args.subparser_name:
        # dispatch subparser handler
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
