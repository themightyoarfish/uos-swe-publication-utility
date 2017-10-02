Before you start
================

In the current setup, we have BibTeX files for each group member. They should
first be assembled into one BibTex file by use of ``bibtool``. This can be done
like this::

    bibtool -Aa -d -f short -s -i *.bib -o all/all.bib
            ^    ^  ^        ^  ^
            |    |  |        |  |
            |-alphanumeric disambiguation 
                 |  |        |  |
                 |  |-generate new short keys
                 |           |  |
                 |-comment out duplicate entries
                             |  |
                             |  |-input files
                             |
                             |-sort ascending

The resulting BibTeX file can then be fed to Publipy.


Command Line Interface
======================

Publipy currently has three subcommands to ``build``, ``list``, and ``add``
bibliography data.

Building a database
-------------------

Before anything else, bibliography data must be imported into publipy via
``publipy build``. The options are such:

.. option:: -d <DATABASE>, --database <DATABASE>

    Path to ``.bib`` file with all entries

.. option:: -p <PDF_LOC>, --pdfs <PDF_LOC>
    
    Path to pdf folder.

This will rekey all entries (since collisions from the Bibtool pass may have led
to similar keys) and read all pdf files from the pdf directory. The files inside
should be named with the key of their associated publication.
The command will create the following directories under the one in which the
database file is located

* ``bib`` - Contains singular BibTeX files for each entry
* ``abstract`` - Contains abstracts of all publications which possess this field
* ``pdf`` For each pdf file whose name is a key in the database, a new file will be placed here

In every case, a file's its name will reflect the new key which its BibTeX entry was given.

``build`` ing a database will add the fields ``publipy_biburl``,
``publipy_pdfurl``, and ``publipy_abstracturl`` and assign the paths to the
files created in the above directories, so that in the html output, proper links
can be generated.

Exporting a database
--------------------

Publipy can export to different formats:

* HTML - Items are wrapped in ``<dd>`` tags
* TeX - A LaTeX document is generated which when compiled contains the
  bibliography data
* BibTeX

The ``list`` subcommand understands these options
 
.. option:: -f {bib,html,tex,pdf}, --format {bib,html,tex}
    
    Format to output.

.. option::  -o OUT, --out OUT    

    File to write to. The appropriate extension is automatically appended, if
    not given in the name.

.. option::  -e EXPR, --expr EXPR 
    
    Filter with python expression. A variable ``entry`` denotes the entry to
    consider. This is currently insecure, since it calls ``eval()`` on the
    input.

.. option::  -p PERSON, --person PERSON

    Print only publications this person is involved in (be
    it author or editor). Currently, there is no fuzzy matching, so the name
    (including middle names) must be exact.

.. option::  -m MYTYPE, --mytype MYTYPE

    Print only publications that have this ``mytype`` value.

.. option::  -c, --complete_html  

    Whether or not to produce valid HTML or only the <dl> element to place
    inside another document. Ignored in any format except html

.. option::  -g GROUPBY, --groupby GROUPBY

    Group resulting publications into sections. The argument is the field to
    group on.  Items which don't have this field are lumped together into an
    ``n/a`` category.

.. option::  -b BIBFILE, --bibfile BIBFILE

    Name of the file to reference in the tex file. Must be
    generated separately (e.g. by use of ``publipy list``).

.. option::  -t TEMPLATE, --template TEMPLATE

    Name of the jinja2 LaTeX template. You can use a custom one if desired.
