'''
Global data that must be passed to plugins. This is a crutch for circumventing
the fact that Pybtex (or setuptools plugins) do not allow passing constructor
arguments to the plugins.

.. py:data:: plugin_data

    A global :py:class:`dict` with the following fields

        * ``label_start``, ``int``: Start value for the labels in a section.
          This value can be updated by the labeling plugin so that numbers are
          consecutive over sections.
        * ``mapping_<key>``, :py:class:`OrderedDict`: Dictionaries for mapping
          section names (which by default are the different values for the key
          to group on) to different strings. The order of the names sets the
          order in the output.
'''

from collections import OrderedDict

plugin_data = {
    'label_start': 10,
    'write_html_wrapper': True,
    # provide key -> name mappings and an order
    'mapping_mytype': OrderedDict([('JOURNAL', 'Journals'),
                                   ('CONFERENCE', 'Conferences'),
                                   ('WORKSHOP', 'Workshops'),
                                   ('EDITEDVOLUME', 'Edited Volumes'),
                                   ('BOOK', 'Books'),
                                   ('CHAPTER', 'Book chapters'),
                                   ('THESIS', 'Theses'),
                                   ('TECHNICALREPORT', 'Technical reports'),
                                   ('OTHER', 'Other'),
                                   ('n/a', 'Unknown')
                                   ])
}
