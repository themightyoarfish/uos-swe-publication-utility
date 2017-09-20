from pybtex.backends.html import Backend as HTMLBackend

class Backend(HTMLBackend):

    def write_entry(self, key, label, text):
        # TODO: If CSS fails, do HTML stuff here
        self.output(u'<dt>%s</dt>\n' % label)
        self.output(u'<dd>%s</dd>\n' % text)
