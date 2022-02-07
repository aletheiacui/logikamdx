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

LOGIKA_INLINE_RE = r'(\*{3}|\*{2}|\*{1}|\_{3}|\_{2}|\_{1}|\-{2}|\+{2})(.+?)\2'
LOGIKA_INLINE_RE_ = re.compile(r'(.*?)(\*{3}|\*{2}|\*{1}|\_{3}|\_{2}|\_{1}|\-{2}|\+{2})(.+?)\2(.*)')

class LogikaInlinePattern(Pattern):

    def handleMatch(self, m):
        tag = self._get_tag(m.group(2))

        if tag == "":
            return m.group(2) + m.group(3) + m.group(2)
        inner_m = LOGIKA_INLINE_RE_.match(m.group(3))

        # Create the Element
        if "," in tag:
            tags = [t.strip() for t in tag.split(",")]
            el = etree.Element(tags[0])
            subtree = etree.SubElement(el, tags[-1])
            if not inner_m:
                subtree.text = m.group(3)
                return el
        else:
            el = etree.Element(tag)
            if not inner_m:
                el.text = m.group(3)
                return el

        tag = self._get_tag(inner_m.group(2))
        if tag == "" or tag == el.tag:
            el.text = m.group(3)
            return el
        el.text = inner_m.group(1)
        subtree = etree.SubElement(el, tag)
        subtree.text = inner_m.group(3)
        subtree.tail = inner_m.group(4)
        return el

    def _get_tag(self, pattern):
        # return html tag based on pattern
        tag = ""
        if pattern == '***' or pattern == '___':
            tag = 'strong,em'
        elif pattern == '**' or pattern == '__':
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