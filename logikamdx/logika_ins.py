from markdown.inlinepatterns import InlineProcessor
from markdown.extensions import Extension
import xml.etree.ElementTree as etree


class InsInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        el = etree.Element('ins')
        el.text = m.group(1)
        return el, m.start(0), m.end(0)

class InsExtension(Extension):
    def extendMarkdown(self, md):
        INS_PATTERN = r'\+\+(.*?)\+\+'  # like ++del++
        md.inlinePatterns.register(InsInlineProcessor(INS_PATTERN, md), 'ins', 176)

def makeExtension(**kwargs):
    return InsExtension(**kwargs)