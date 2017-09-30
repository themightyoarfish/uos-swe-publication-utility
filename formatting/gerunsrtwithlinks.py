import locale
import datetime
import pybtex

from unsrtwithlinks import Style as UnsrtStyle
from pybtex.style.template import (field, sentence, names, join, words,
                                   optional, together, optional_field, first_of)
from pybtex.style.formatting.unsrt import dashify
from pybtex.richtext import Symbol


def localize_month(m):
    # not sure how else to do it; how does apply_func work?
    try:
        month_num = datetime.datetime.strptime(str(m), "%B")
    except ValueError:
        # strange strings
        return ''
    locale.setlocale(locale.LC_ALL, 'de_DE')
    month = datetime.datetime.strftime(month_num, '%B')
    locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())
    return month


date = words[optional_field('month',
                            apply_func=lambda x: localize_month(x)),
             field('year')]

# use new date instead of module-level function from unsrt.py
pybtex.style.formatting.unsrt.date = date


class Style(UnsrtStyle):
    """Style for appending links to html output."""

    def format_names(self, role, as_sentence=True):
        """Override for german"""
        formatted_names = names(role, sep=', ', sep2=' und ', last_sep=' und ')
        if as_sentence:
            return sentence[formatted_names]
        else:
            return formatted_names

    def format_editor(self, e, as_sentence=True):
        """Override for german"""
        editors = self.format_names('editor', as_sentence=False)
        if 'editor' not in e.persons:
            # when parsing the template, a FieldIsMissing exception
            # will be thrown anyway; no need to do anything now,
            # just return the template that will throw the exception
            return editors
        word = 'Hrsg.'
        result = join(sep=', ')[editors, word]
        if as_sentence:
            return sentence[result]
        else:
            return result

    def format_volume_and_series(self, e, as_sentence=True):
        volume_and_series = optional[
            words[
                together['Band', field('volume')], optional[
                    words['von', field('series')]
                ]
            ]
        ]
        number_and_series = optional[
            words[
                join(sep=Symbol('nbsp'))['Nr.' if as_sentence else 'nr.',
                                         field('number')],
                optional[
                    words['in', field('series')]
                ]
            ]
        ]
        series = optional_field('series')
        result = first_of[
            volume_and_series,
            number_and_series,
            series,
        ]
        if as_sentence:
            return sentence(capfirst=True)[result]
        else:
            return result

    def format_chapter_and_pages(self, e):
        pages = field('pages', apply_func=dashify)
        return join(sep=', ')[
            optional[together['Kapitel', field('chapter')]],
            optional[together['p.', pages]],
        ]

    def format_edition(self, e):
        return optional[
            words[
                field('edition', apply_func=lambda x: x.lower()),
                'Auflage',
            ]
        ]
