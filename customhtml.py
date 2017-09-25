import pybtex
from pybtex.backends.html import Backend as HTMLBackend
from plugin_data import plugin_data

PROLOGUE = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
<head><meta name="generator" content="Pybtex">
<meta http-equiv="Content-Type" content="text/html; charset={encoding}">
<title>Bibliography</title>
<style>
{stylesheet}
</style>
</head>
<body>
<dl>
'''

with open('publications.css') as css_file:
    STYLESHEET = css_file.read()


class Backend(HTMLBackend):

    def write_entry(self, key, label, text):
        # TODO: If CSS fails, do HTML stuff here
        self.output(u'<dt>%s</dt>\n' % label)
        self.output(u'<dd>%s</dd>\n' % text)

    def write_epilogue(self):
        if plugin_data['write_html_wrapper']:
            super().write_epilogue()
        else:
            pass

    def write_prologue(self):
        if plugin_data['write_html_wrapper']:
            encoding = self.encoding or pybtex.io.get_default_encoding()
            self.output(PROLOGUE.format(encoding=encoding,
                                        stylesheet=STYLESHEET))
        else:
            pass
