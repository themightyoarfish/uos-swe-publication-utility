import pybtex
from pybtex.backends.html import Backend as HTMLBackend

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

STYLESHEET = r'''dl {
    width: 100%;
    overflow: hidden;
    padding: 0;
    margin: 0
}
dt {
    float: left;
    width: 5%;
    padding: 0;
    margin: 0;
    text-align: center;
}
dt::before {
    content: "["
}
dt::after {
    content: "]"
}
dd {
    float: left;
    width: 95%;
    padding: 0;
    margin: 0;
    margin-bottom: 1em
}'''


class Backend(HTMLBackend):

    def write_entry(self, key, label, text):
        # TODO: If CSS fails, do HTML stuff here
        self.output(u'<dt>%s</dt>\n' % label)
        self.output(u'<dd>%s</dd>\n' % text)

    def write_prologue(self):
        encoding = self.encoding or pybtex.io.get_default_encoding()
        self.output(PROLOGUE.format(encoding=encoding, stylesheet=STYLESHEET))
