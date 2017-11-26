from collections import OrderedDict
# dirty global fields, but no way to pass args to LabelStyle or other plugin :|
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
