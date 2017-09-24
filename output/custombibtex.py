from pybtex.database.output.bibtex import Writer as BibTexWriter


class Writer(BibTexWriter):

    def _encode(self, text):
        """Override to avoid treating incoming strings as utf8 instead of latex.
        Pybtex assumes the text passed in is not already latex, but that is
        usually incorrext, since bibtex may include latex escape sequences. We
        thus need to drop the call to self._encode
        """
        return text
