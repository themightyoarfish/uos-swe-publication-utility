from setuptools import setup
"""
Install pybtex style plugin
"""

setup(name='Pybtex HTML rendering extensions',
      author='Rasmus Diederichsen',
      py_modules=['unsrtwithlinks'],
      entry_points={
          'pybtex.style.formatting': ['unsrtwithlinks = unsrtwithlinks:Style',
                                      'gerunsrtwithlinks =\
                                      gerunsrtwithlinks:Style'
                                      ],
          'pybtex.backends': 'customhtml = customhtml:Backend',
          'pybtex.style.labels': 'numberwithoffset = labels.numberwithoffset:LabelStyle',
      },
)
