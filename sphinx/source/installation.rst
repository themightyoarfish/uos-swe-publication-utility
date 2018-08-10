Setup
======

Publipy builds on `Pybtex <https://docs.pybtex.org/index.html>`_, a BibTeX
library for python. Pybtex supports `Setuptools plugins <https://setuptools.readthedocs.io/en/latest/setuptools.html#extensible-applications-and-frameworks>`_ which can be supplied by clients in order to define e.g.

* backends for new output formats or handling of existing formats (Publipy uses a ``customhtml`` plugin to modify html output)
* styles for defining (output format-agnostic) styles (Publipy uses
  ``unsrtwithlinks`` styles for adding hyperlinkst to the classic UNSRT citation
  style and also ships a German version of the style)
* label styles for defining how labels are rendered
* sorting plugins for influencing the order of bibliography items

Before running Pybtex, the plugins must be installed by::

    sudo python3 setup.py install

Furthermore, all necessary requirements should be installed via::

    sudo pip3 install -r requirements.txt

or::
    
    pip3 install --user -r requirements.txt

to install without root priviliges.


For creating new plugins, consult the ``setup.py`` file and the Pybtex
documentation.
