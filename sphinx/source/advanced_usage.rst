Advanced Usage
==============

Changing section titles
^^^^^^^^^^^^^^^^^^^^^^^

If you would like to group by an attribute, but not use the attribute's
different values as section titles in the output, you may edit
:py:mod:`plugin_data` to include a ``mapping_<key>`` for your grouping attribute::
  
    plugin_data = {
        ...
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

