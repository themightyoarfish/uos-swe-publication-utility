from setuptools import setup
"""
Install pybtex style plugin
"""

setup(name='Pybtex HTML rendering extensions',
      author='Rasmus Diederichsen',
      entry_points={
          'pybtex.style.formatting': ['gerunsrtwithlinks = formatting.gerunsrtwithlinks:Style',
                                      'unsrtwithlinks = formatting.unsrtwithlinks:Style',
                                      'myunsrt = formatting.myunsrt:Style'],
          'pybtex.backends': 'customhtml = backends.customhtml:Backend',
          'pybtex.style.labels': 'numberwithoffset = labels.numberwithoffset:LabelStyle',
          'pybtex.style.sorting': ['custom_author_year_title = sorting.custom_author_year_title:SortingStyle',
                                   'year_author = sorting.year_author:SortingStyle'
                                   ],
          'pybtex.database.output': 'custombibtex = output.custombibtex:Writer',
      },
      )
