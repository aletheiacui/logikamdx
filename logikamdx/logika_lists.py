"""
Logika Extension for Python-Markdown
=======================================
Modification of Sane Lists in Python-Markdown extension.
See <https://Python-Markdown.github.io/extensions/sane_lists>
for documentation.

Original code Copyright 2011 [Waylan Limberg](http://achinghead.com)
Changes Copyright 2011-2014 The Python Markdown Project

Subsequent changes Copyright 2022 Philologika LLC

License: [BSD](https://opensource.org/licenses/bsd-license.php)
"""

import re
import string
import xml.etree.ElementTree as etree

from markdown.blockprocessors import OListProcessor, UListProcessor
from markdown.extensions import Extension

class SaneOListProcessor(OListProcessor):

    SIBLING_TAGS = ['ol']
    LAZY_OL = False

    def __init__(self, parser):
        super().__init__(parser)
        self.CHILD_RE = re.compile(r'^[ ]{0,%d}((\d+\.))[ ]+(.*)' %
                                   (self.tab_length - 1))
    

class LogikaUListProcessor(UListProcessor):

    SIBLING_TAGS = ['ul']

    def __init__(self, parser):
        super().__init__(parser)
        self.CHILD_RE = re.compile(r'^[ ]{0,%d}(([*+-]))[ ]+(.*)' %
                                   (self.tab_length - 1))


class LogikaOListProcessor(OListProcessor):
    SIBLING_TAGS = ['ol']
    LAZY_OL = False

    def __init__(self, parser):
        super().__init__(parser)
        self.list_style = "style:decimal;"

        self.LOGIKA_INDENT_RE = re.compile(r'^[ ]{%d,%d}((\d+\.)|([a-z]+\.)|([A-Z]+\.)|[*+-])[ ]+.*' % (self.tab_length, self.tab_length * 2 - 1))
        self.STARTSWITH_RE = re.compile(r'(\d+)')
    
    def run(self, parent, blocks):
        # Check fr multiple items in one block.
        items = self.get_items(blocks.pop(0))
        sibling = self.lastChild(parent)
        if sibling is not None and sibling.tag in self.SIBLING_TAGS and sibling.attrib['style'] == self.list_style:
            # Previous block was a list item, so set that as parent
            lst = sibling
            # make sure previous item is in a p- if the item has text,
            # then it isn't in a p
            if lst[-1].text:
                # since it's possible there are other children for this
                # sibling, we can't just SubElement the p, we need to
                # insert it as the first item.
                p = etree.Element('p')
                p.text = lst[-1].text
                lst[-1].text = ''
                lst[-1].insert(0, p)
            # if the last item has a tail, then the tail needs to be put in a p
            # likely only when a header is not followed by a blank line
            lch = self.lastChild(lst[-1])
            if lch is not None and lch.tail:
                p = etree.SubElement(lst[-1], 'p')
                p.text = lch.tail.lstrip()
                lch.tail = ''

            # parse first block differently as it gets wrapped in a p.
            li = etree.SubElement(lst, 'li')
            self.parser.state.set('looselist')
            firstitem = items.pop(0)
            self.parser.parseBlocks(li, [firstitem])
            self.parser.state.reset()

        elif parent.tag in ['ol', 'ul'] and parent.attrib['style'] == self.list_style:
            # this catches the edge case of a multi-item indented list whose
            # first item is in a blank parent-list item:
            # * * subitem1
            #     * subitem2
            # see also ListIndentProcessor
            lst = parent
        else:
            # This is a new list so create parent with appropriate tag.
            lst = etree.SubElement(parent, self.TAG)
            # Check if a custom start integer is set
            if not self.LAZY_OL and self.STARTSWITH != '1':
                lst.attrib['start'] = self.STARTSWITH

        lst.set("style", self.list_style)

        self.parser.state.set('list')
        # Loop through items in block, recursively parsing each with the
        # appropriate parent.
        for item in items:
            if item.startswith(' '*self.tab_length):
                # Item is indented. Parse with last item as parent
                self.parser.parseBlocks(lst[-1], [item])
            else:
                # New item. Create li and parse with it as parent
                li = etree.SubElement(lst, 'li')
                self.parser.parseBlocks(li, [item])
        self.parser.state.reset()
    
    def _set_first_value(self, m):
        self.STARTSWITH = self.STARTSWITH_RE.match(m.group(1)).group()

    def get_items(self, block):
        """ Break a block into list items. """
        items = []
        for line in block.split('\n'):
            m = self.CHILD_RE.match(line)
            if m:
                # This is a new list item
                # Check first item for the start index
                if not items and self.TAG == 'ol':
                    # Detect the integer value of first list item
                    self._set_first_value(m)
                # Append to the list
                items.append(m.group(3))

            elif self.LOGIKA_INDENT_RE.match(line):
                # This is an indented (possibly nested) item.
                if items[-1].startswith(' '*self.tab_length):
                    # Previous item was indented. Append to that item.
                    items[-1] = '{}\n{}'.format(items[-1], line)
                else:
                    items.append(line)
            else:
                # This is another line of previous item. Append to that item.
                items[-1] = '{}\n{}'.format(items[-1], line)
        return items


class LowerAlphaListProcessor(LogikaOListProcessor):
    def __init__(self, parser):
        super().__init__(parser)
        self.list_style = "style:lower-alpha;"
        self.STARTSWITH_RE = re.compile(r'([a-z]+)')
        self.RE = re.compile(r'^[ ]{0,%d}[a-z]+\.[ ]+(.*)' % (self.tab_length - 1))
        # Detect items on secondary lines. they can be of either list type.
        self.CHILD_RE = re.compile(r'^[ ]{0,%d}(([a-z]+\.))[ ]+(.*)' %
                                   (self.tab_length - 1))

    def _set_first_value(self, m):
        starting_letter = self.STARTSWITH_RE.match(m.group(1)).group()
        self.STARTSWITH = str(string.ascii_lowercase.index(starting_letter) + 1)


class UpperAlphaListProcessor(LogikaOListProcessor):
    def __init__(self, parser):
        super().__init__(parser)
        self.list_style = "style:upper-alpha;"
        self.STARTSWITH_RE = re.compile(r'([A-Z]+)')
        self.RE = re.compile(r'^[ ]{0,%d}[A-Z]+\.[ ]+(.*)' % (self.tab_length - 1))
        # Detect items on secondary lines. they can be of either list type.
        self.CHILD_RE = re.compile(r'^[ ]{0,%d}(([A-Z]+\.))[ ]+(.*)' %
                                   (self.tab_length - 1))

    def _set_first_value(self, m):
        starting_letter = self.STARTSWITH_RE.match(m.group(1)).group()
        self.STARTSWITH = str(string.ascii_uppercase.index(starting_letter) + 1)


class LowerRomanOListProcessor(LogikaOListProcessor):

    SIBLING_TAGS = ['ol']
    LAZY_OL = False

    ROMAN_LOWER_RE = re.compile('(m{0,4}(cm|cd|d?c{0,3})(xc|xl|l?x{0,3})(ix|iv|v?i{0,3}))')

    def __init__(self, parser):
        super().__init__(parser)
        self.list_style = "list-style-type:lower-roman;"
        self.STARTSWITH_RE = re.compile(r'(m{0,4}(?:cm|cd|d?c{0,3})(?:xc|xl|l?x{0,3})(?:ix|iv|v?i{0,3}))')
        self.RE = re.compile(r'^[ ]{0,%d}m{0,4}(?:cm|cd|d?c{0,3})(?:xc|xl|l?x{0,3})(?:ix|iv|v?i{0,3})\.[ ]+(.*)' % (self.tab_length - 1))
        # Detect items on secondary lines. they can be of either list type.
        self.CHILD_RE = re.compile(r'^[ ]{0,%d}((m{0,4}(?:cm|cd|d?c{0,3})(?:xc|xl|l?x{0,3})(?:ix|iv|v?i{0,3})\.))[ ]+(.*)' %
                                   (self.tab_length - 1))

    def _set_first_value(self, m):
        s = self.STARTSWITH_RE.match(m.group(1)).group()
        rom_val = {'i': 1, 'v': 5, 'x': 10, 'l': 50, 'c': 100, 'd': 500, 'm': 1000}
        int_val = 0
        for i in range(len(s)):
            if i > 0 and rom_val[s[i]] > rom_val[s[i - 1]]:
                int_val += rom_val[s[i]] - 2 * rom_val[s[i - 1]]
            else:
                int_val += rom_val[s[i]]

        self.STARTSWITH = str(int_val)


class UpperRomanOListProcessor(LogikaOListProcessor):

    ROMAN_UPPER_RE = re.compile('(M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}))')

    def __init__(self, parser):
        super().__init__(parser)
        self.list_style = "list-style-type:upper-roman;"
        self.STARTSWITH_RE = re.compile(r'(M{0,4}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3}))')
        self.RE = re.compile(r'^[ ]{0,%d}M{0,4}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})\.[ ]+(.*)' % (self.tab_length - 1))
        # Detect items on secondary lines. they can be of either list type.
        self.CHILD_RE = re.compile(r'^[ ]{0,%d}((M{0,4}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})\.))[ ]+(.*)' %
                                   (self.tab_length - 1))
    
    def _set_first_value(self, m):
        s = self.STARTSWITH_RE.match(m.group(1)).group()
        rom_val = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        int_val = 0
        for i in range(len(s)):
            if i > 0 and rom_val[s[i]] > rom_val[s[i - 1]]:
                int_val += rom_val[s[i]] - 2 * rom_val[s[i - 1]]
            else:
                int_val += rom_val[s[i]]

        self.STARTSWITH = str(int_val)
    

class LogikaListExtension(Extension):
    """ Add sane lists to Markdown. """

    def extendMarkdown(self, md):
        """ Override existing Processors. """
        md.parser.blockprocessors.register(LogikaOListProcessor(md.parser), 'olist', 40)
        md.parser.blockprocessors.register(LogikaUListProcessor(md.parser), 'ulist', 30)
        md.parser.blockprocessors.register(LowerAlphaListProcessor(md.parser), 'loweralphalist', 31)
        md.parser.blockprocessors.register(UpperAlphaListProcessor(md.parser), 'upperalphalist', 31)
        md.parser.blockprocessors.register(LowerRomanOListProcessor(md.parser), 'lowerromanlist', 35)
        md.parser.blockprocessors.register(UpperRomanOListProcessor(md.parser), 'upperromanlist', 35)
        

def makeExtension(**kwargs):  # pragma: no cover
    return LogikaListExtension(**kwargs)
