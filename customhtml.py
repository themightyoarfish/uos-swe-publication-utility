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
        self.output('<dt>%s</dt>\n' % label)
        self.output('<dd>%s</dd>\n' % text)

    def write_section(self, text):
        self.output('<h2 class="publipy-section">%s</h2>' % text)

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

    def write_to_file(self, formatted_entries, filename):
        with pybtex.io.open_unicode(filename, "w", self.encoding) as stream:
            self.write_to_stream(formatted_entries, stream)
            if hasattr(stream, 'getvalue'):
                return stream.getvalue()

    def write_to_stream(self, formatted_bibliography, stream):
        self.output = stream.write
        self.formatted_bibliography = formatted_bibliography

        self.write_prologue()
        entries = list(formatted_bibliography)
        last_group = None
        if len(entries) == 0:
            pass
        else:
            if isinstance(entries[0], tuple):
                for group_name, entry in entries:
                    if group_name != last_group:
                        self.write_section(group_name)
                    last_group = group_name
                    self.write_entry(entry.key, entry.label, entry.text.render(self))
            else:
                for entry in entries:
                    self.write_entry(entry.key, entry.label, entry.text.render(self))
        self.write_epilogue()
