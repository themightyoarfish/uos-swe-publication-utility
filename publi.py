#!/usr/bin/env python3
import argparse
import json
from itertools import combinations
import pybtex.database
from pickle import load, dump

databases_file = "databases.json"

class PublicationDatabase(object):
    """Class to hold information about publiction lists"""

    @classmethod
    def default_comparator(cls, item1, item2):
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

    def __init__(self, databases_file):
        """Create a database by reading all the .bib files listed in a file"""
        self.databases_file = databases_file
        self.populate(databases_file)

    def delete(self, key):
        for member, publications in self.publications.items():
            for k, entry in publications.entries.items():
                if k == key:
                    # dirty hack since CaseInsensitiveOrderedDict does not
                    # support deletion
                    del publications.entries.__dict__['_dict'][k]
                    import ipdb; ipdb.set_trace()


    def save(self):
        with open('db.pckl', mode='wb') as f:
            dump(self.publications, f)

    def load(self):
        with open('db.pckl', mode='rb') as f:
            self.publications = load(f)

    def populate(self, databases_file):
        """Collect all bibdata from all files into one big-ass database"""

        with open(databases_file) as file:
            databases = json.load(file)
            # db has entries of (author: foo, path: bar), which we obtain by
            # asking the dict for its values (removing the keys) and turning
            # them into tuples so we can do (a,b) = tup on them in the dict
            # comprehension below. Why not just use d.values() in lambda? Because
            # the order is non-deterministic
            self.publications = {
                    member: read_bibfile(bibloc)
                        for (member, bibloc) in map(lambda d: (d['author'], d['path']), databases['files'])
            }

    def find_duplicates(self, comparator=None):
        """Find suspected duplicates"""
        if not comparator:
            comparator = PublicationDatabase.default_comparator
        suspects = []
        for _, publications in self.publications.items():
            # it seems that OrderedCaseInsensitiveDict, which inherits from
            # MutableMapping, does not provide an items() iterator, so we need
            # to form tuples manually
            combos = combinations([(key, publications.entries[key]) for key in publications.entries], 2)
            for (item1, item2) in combos:
                if comparator(item1, item2):
                    suspects.append((item1, item2))
        return suspects


def build(args):
    pubdata = PublicationDatabase(args.databases)
    duplicates = pubdata.find_duplicates()
    pubdata.delete('iyenghar.pulvermueller.ea:model-based*1')
    pubdata.save()
    print("Suspected duplicates: ")
    for item1, item2 in duplicates:
        print("\t{} == {}".format(item1[0], item2[0]))

def add(args):
    pass

def read_bibfile(filename):
    with open(filename) as f:
        return pybtex.database.parse_file(f, 'bibtex')

def deduplicate(database):
    pass

def render_to_latex(bibdata, template):
    pass

def render_to_html(bibdata):
    pass

def build_publication_map(bibdata, pdf_paths=[]):
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
            help='json file with absolute paths to all relevant bibtex files')
    build_parser.set_defaults(func=build)

    ############################################################################
    #                             add subcommand                               #
    ############################################################################
    add_parser = subparsers.add_parser('add', help='Add something to the database')
    add_parser.add_argument('-e', '--entry', required=False, type=str,
            help='bibtex entry to add')
    add_parser.add_argument('-m', '--member', required=True, type=str,
            help='name of the group member to add the publication to')
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
