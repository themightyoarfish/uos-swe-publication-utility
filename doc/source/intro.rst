Overview
===========
publipy is a bibliography tool developed for the Software Engineering group at
Osnabrück University. It can do the following things:

* Read a set of ``BibTeX`` files to compile a monolithic database (use the
  ``build`` subcommand)

    * Remove suspected duplicates (todo)
    * Generated useful and unique keys
    * From a directory of pdfs whose file names are the original keys of
      bibliohraphy entries, create a new directory with all pdfs inside, renamed
      to the appropriate keys

* Render select portions of the bibliography to various formats, such as TeX,
  HTML, or BibTeX (use the ``list`` subcommand)

    * Arbirary filter expressions are supported
    * Convenience options for filtering based on person are supported
    * Resulting entries (in HTML and TeX) can be grouped by another criterion

* Add new bibliograpy entries to the database and have them moved to the correct
  location and assigned a new key (use the ``add`` subcommand)

Source
======
The tool can be found at `Github <https://github.com/themightyoarfish/uos-swe-publication-utility>`_.

