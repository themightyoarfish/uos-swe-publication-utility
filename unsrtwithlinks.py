from pybtex.style.formatting.unsrt import Style as UnsrtStyle
from pybtex.style import FormattedEntry
from pybtex.richtext import Text, String, HRef, Tag


class Style(UnsrtStyle):
    """Style for appending links to html output."""

    def format_entries(self, entries):
        """Override for appending links before yielding FormattedEntries.
        :param entries: `BibliographyData` entries
        :type entries:  BibliographyData
        """
        sorted_entries = self.sort(entries)
        labels = self.format_labels(sorted_entries)
        for label, entry in zip(labels, sorted_entries):
            for persons in entry.persons.itervalues():
                for person in persons:
                    person.text = self.format_name(person, self.abbreviate_names)

            f = getattr(self, "format_" + entry.type)
            text = f(entry)
            # TODO: Add links to entries and query here
            text = text + Text(String('['), HRef('foo://bar', Tag('tt', 'pdf')),
                               String(']'))
            yield FormattedEntry(entry.key, text, label)
