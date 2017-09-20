from pybtex.style.formatting.unsrt import Style as UnsrtStyle
from pybtex.style.template import field, sentence
from pybtex.style import FormattedEntry
from pybtex.richtext import Text, String, HRef, Tag


class Style(UnsrtStyle):
    """Style for appending links to html output."""

    def format_title(self, e, which_field, as_sentence=True):
        formatted_title = field(
            which_field
        )

        if as_sentence:
            return sentence(capfirst=False) [ formatted_title ]
        else:
            return formatted_title

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
                    person.text = self.format_name(person,
                                                   self.abbreviate_names)

            # if 'title' in entry.fields and 'Geodatenvisualisierung' in
            # entry.fields['title']: import ipdb; ipdb.set_trace()
            f = getattr(self, "format_" + entry.type)
            text = f(entry)
            text = text + Text(String(' ['),
                               HRef(entry.fields['publipy_biburl'],
                                    Tag('tt', 'bib')),
                               String('] ')
                               )
            text = text + Text(String(' ['),
                               HRef(entry.fields['publipy_pdfurl'],
                                    Tag('tt', 'pdf')),
                               String(']')
                               )
            if 'publipy_abstracturl' in entry.fields:
                text = text + Text(String(' ['),
                                   HRef(entry.fields['publipy_abstracturl'],
                                        Tag('tt', 'abstract')),
                                   String(']')
                                   )
            yield FormattedEntry(entry.key, text, label)
