from pybtex.style.sorting.author_year_title import (SortingStyle as
                                                    AuthorYearSortingStyle)


class SortingStyle(AuthorYearSortingStyle):
    """Override because author-year style maps distinct items to the same
    key."""

    def sort(self, entries):
        """Remove same-key bug here."""
        keys_entries = [(self.sorting_key(entry), entry) for entry in entries]
        entry_dict = {}
        for key, entry in keys_entries:
            c = 1
            # TODO: Is this really correct?
            newkey = list(key) + ['']
            while tuple(newkey) in entry_dict:
                newkey[:-1] = '*%d' % c     # append something while not unique
                c += 1
            entry_dict[tuple(newkey)] = entry
        sorted_keys = sorted(entry_dict)
        sorted_entries = [entry_dict[key] for key in sorted_keys]
        return sorted_entries
