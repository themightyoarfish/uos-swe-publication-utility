from pybtex.style.sorting.author_year_title import (SortingStyle as
                                                    AuthorYearSortingStyle)
from dateutil import parser
from datetime import datetime

def extract_month(month_str):
    '''Get the first thing which parses as a month. Will only find months at the
    beginning of the string.'''
    if len(month_str) < 3:
        return None
    for l in range(3, len(month_str)):
        try:
            month = parser.parse(month_str[:l+1]).month
            return month
        except ValueError:
            continue

class SortingStyle(AuthorYearSortingStyle):
    '''A sorting style that prioritizes the publication date over title and
    author. Sorting is in descending order. More specific dates (i.e. with month
    as opposed to year only) are given precedence.'''

    def sorting_key(self, entry):
        year = 2017
        month = 1
        day = 1
        if 'year' in entry.fields:
            year = int(entry.fields['year'])
        if 'month' in entry.fields:
            month = extract_month(entry.fields['month']) or 1

        date_key = datetime(year=year, month=month, day=day)

        # this part is simply the same functionality as in the builtin
        # author_year_title style; at the end we inject the year at the
        # beginning
        if entry.type in ('book', 'inbook'):
            author_key = self.author_editor_key(entry)
        elif 'author' in entry.persons:
            author_key = self.persons_key(entry.persons['author'])
        else:
            author_key = ''

        return (date_key, author_key, entry.fields.get('title', ''))

    def sort(self, entries):
        keys_entries = [(self.sorting_key(entry), entry) for entry in entries]
        # disambiguate
        entry_dict = {}
        for key, entry in keys_entries:
            c = 1
            newkey = list(key)
            title_field = key[-1] + '*'
            while tuple(newkey) in entry_dict:
                title_field += '%d' % c     # append something while not unique
                newkey[-1] = title_field
                c += 1
            entry_dict[tuple(newkey)] = entry
        sorted_keys = reversed(sorted(entry_dict))
        sorted_entries = [entry_dict[key] for key in sorted_keys]
        return sorted_entries
