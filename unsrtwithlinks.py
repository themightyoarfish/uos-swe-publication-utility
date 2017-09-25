from pybtex.style.formatting.unsrt import Style as UnsrtStyle
from pybtex.style.template import field, sentence, href, join, optional, tag
from pybtex.style import FormattedEntry
from pybtex.plugin import find_plugin
from plugin_data import plugin_data


class Style(UnsrtStyle):
    """Style for appending links to html output."""

    def __init__(self, label_style=None, name_style=None, sorting_style=None,
                 abbreviate_names=False, min_crossrefs=2, **kwargs):

        if not label_style:
            # must be done before calling super()
            label_style = find_plugin('pybtex.style.labels', 'numberwithoffset')
        label_style.label_start = plugin_data['label_start']

        super().__init__(label_style=label_style, name_style=name_style,
                         sorting_style=sorting_style,
                         abbreviate_names=abbreviate_names,
                         min_crossrefs=min_crossrefs, **kwargs)

    def format_title(self, e, which_field, as_sentence=True):
        formatted_title = field(
            which_field
        )

        if as_sentence:
            return sentence(capfirst=False)[formatted_title]
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

            f = getattr(self, "format_" + entry.type)
            text = f(entry)

            bib = optional[
                join['[',
                     tag('tt')[
                         href[
                             field('publipy_biburl', raw=True),
                             'bib'
                         ]
                     ],
                     ']'
                     ]
            ]

            pdf = optional[
                join['[',
                     tag('tt')[
                         href[
                             field('publipy_pdfurl', raw=True),
                             'pdf'
                         ]
                     ],
                     ']'
                     ]
            ]

            abstract = optional[
                join['[',
                     tag('tt')[
                         href[
                             field('publipy_abstracturl', raw=True),
                             'abstract'
                         ]
                     ],
                     ']'
                     ]
            ]

            www = join['[',
                       tag('tt')[
                           href[
                               field('url_home', raw=True),
                               'www'
                           ]
                       ],
                       ']'
                       ]

            text += ' '  # make some space
            if entry.fields['url_home']:
                text += join(sep=' ')[bib, pdf, abstract, www].format_data(entry)
            else:
                text += join(sep=' ')[bib, pdf, abstract].format_data(entry)

            yield FormattedEntry(entry.key, text, label)
