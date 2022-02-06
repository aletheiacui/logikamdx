"""
Logika Extension for Python-Markdown
"""

import markdown

extensions = ['logikamdx.logika_inline',
              'logikamdx.logika_table',
              ]
              

class LogikaExtension(markdown.Extension):
    """ Add Logika extensions to Markdown class."""

    def extendMarkdown(self, md):
        """ Register extension instances. """
        md.registerExtensions(extensions, self.config)
        # Turn on processing of markdown text within raw html
        md.preprocessors['html_block'].markdown_in_raw = True

def makeExtension(**kwargs):
    return LogikaExtension(**kwargs)