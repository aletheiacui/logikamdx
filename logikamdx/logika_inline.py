"""
Logika Inline Display Extension for Python-Markdown
====================================

Modified parsing of inline elements to Python-Markdown.

Copyright 2022 Philologika LLC

License: [BSD](https://opensource.org/licenses/bsd-license.php)
"""

from markdown.inlinepatterns import Pattern
from markdown.extensions import Extension
import xml.etree.ElementTree as etree
import re

# **, __ strong
# *, _ em
# ++ ins
# -- del

LOGIKA_INLINE_RE = r'([\*\_\-\+]{2}|[\*\_]{1})(.*?)\2'
LOGIKA_INLINE_RE_ = r'^([\*\_\-\+]{2}|[\*\_]{1})(.*?)\1$'

class LogikaInlinePattern(Pattern):

    def handleMatch(self, m):
        tag = self._get_tag(m.group(2))

        if tag == "":
            return m.group(2) + m.group(3) + m.group(2)

        # Create the Element
        el = etree.Element(tag)
        inner_m = re.match(LOGIKA_INLINE_RE_, m.group(3))
        if not inner_m:
            el.text = m.group(3)
            return el
        else:
            tag = self._get_tag(inner_m.group(1))
            if tag == "" or tag == el.tag:
                el.text = m.group(3)
                return el
            subtree = etree.SubElement(el, tag)
            subtree.text = inner_m.group(2)

        return el

    def _get_tag(self, pattern):
        # return html tag based on pattern
        tag = ""
        if pattern == '**' or pattern == '__':
            # Bold
            tag = 'strong'
        elif pattern == '*' or pattern == '_':
            # italics
            tag = 'em'
        elif pattern == '++':
            # Underline
            tag = 'ins'        
        elif pattern == '--':
            # Strike
            tag = 'del'
        
        return tag

class LogikaInlineExtension(Extension):
    def extendMarkdown(self, md):
        # Delete the default patterns
        md.inlinePatterns.deregister('em_strong')
        md.inlinePatterns.deregister('em_strong2')
        md.inlinePatterns.deregister('not_strong')

        # Add new patterns
        logika_inline = LogikaInlinePattern(LOGIKA_INLINE_RE)
        md.inlinePatterns['logika_inline'] = logika_inline

def makeExtension(**kwargs):
    return LogikaInlineExtension(**kwargs)