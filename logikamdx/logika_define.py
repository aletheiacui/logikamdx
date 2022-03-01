"""
Logika Inline Display Extension for Python-Markdown
====================================

Copyright 2022 Philologika LLC

License: [BSD](https://opensource.org/licenses/bsd-license.php)
"""

from markdown.inlinepatterns import InlineProcessor
from markdown.extensions import Extension
import xml.etree.ElementTree as etree
import re 

class LogikaDefinePattern(InlineProcessor):
    def handleMatch(self, m, data):
        el = etree.Element("span")
        if m.group(4):
            wordform = m.group(4)
        else:
            wordform = re.sub(r'<.+?>', '', m.group(2))
            wordform = re.sub(r'\-{2}|\+{2}|\*|\_', '', wordform)
            
        el.set("name", wordform)
        el.set("class", "define-wordform")
        el.text = m.group(2)
        return el, m.start(0), m.end(0)

class LogikaDefineExtension(Extension):
    def extendMarkdown(self, md):
        # Add new patterns
        DEFINE_PATTERN = r'(\{(.+?)\})(\((.+)\))?'
        md.inlinePatterns.register(LogikaDefinePattern(DEFINE_PATTERN, md), 'logika_define', 170)


def makeExtension(**kwargs):
    return LogikaDefineExtension(**kwargs)