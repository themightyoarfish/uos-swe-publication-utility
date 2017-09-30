from setuptools import setup
"""
Install pybtex style plugin
"""

setup(name='Pybtex HTML rendering extensions',
      author='Rasmus Diederichsen',
      py_modules=['unsrtwithlinks'],
      entry_points={
          'pybtex.style.formatting': ['unsrtwithlinks = formatting.unsrtwithlinks:Style',
                                      'gerunsrtwithlinks =\
                                      formatting.gerunsrtwithlinks:Style'
                                      ],
          'pybtex.backends': 'customhtml = backends.customhtml:Backend',
          'pybtex.style.labels': 'numberwithoffset = labels.numberwithoffset:LabelStyle',
          'pybtex.style.sorting': 'custom_author_year_title = sorting.custom_author_year_title:SortingStyle',
          'pybtex.database.output': 'custombibtex = output.custombibtex:Writer',
      },
      )
