"""
Logika Inline Display Extension for Python-Markdown
====================================

Copyright 2022 Philologika LLC

License: [BSD](https://opensource.org/licenses/bsd-license.php)
"""

from markdown.inlinepatterns import Pattern
from markdown.extensions import Extension
import xml.etree.ElementTree as etree
from markdown.util import AtomicString
import re

# ++ ins
# -- del

LOGIKA_INLINE_RE = r'(\-{2}|\+{2})(.+?)\2'

class LogikaInlinePattern(Pattern):
    def handleMatch(self, m):
        tag = self._get_tag(m.group(2))

        if tag == "":
            return m.group(2) + m.group(3) + m.group(2)
        # Create the Element
        el = etree.Element(tag)
        el.text = m.group(3)
        return el

    def _get_tag(self, pattern):
        # return html tag based on pattern
        tag = ""
        if pattern == '++':
            # Underline
            tag = 'ins'        
        elif pattern == '--':
            # Strike
            tag = 'del'
        
        return tag

class LogikaInlineExtension(Extension):
    def extendMarkdown(self, md):
        # Add new patterns
        logika_inline = LogikaInlinePattern(LOGIKA_INLINE_RE)
        md.inlinePatterns['logika_inline'] = logika_inline

def makeExtension(**kwargs):
    return LogikaInlineExtension(**kwargs)