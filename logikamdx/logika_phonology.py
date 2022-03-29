"""
Logika Phonology Display Extension for Python-Markdown
====================================

Copyright 2022 Philologika LLC

License: [BSD](https://opensource.org/licenses/bsd-license.php)
"""

from markdown.inlinepatterns import InlineProcessor
from markdown.extensions import Extension
import xml.etree.ElementTree as etree
import re

class LogikaPhonologyProcessor(InlineProcessor):

    PHON_PART = re.compile('^(\s*(\(?\[\[(.*?)\]\])\)?|\s*(->)|\s*(/)|\s*(\_+))')
    IPA_BRACKETS = re.compile('^[/[].+?[]|/]')

    def handleMatch(self, m, data):
        # Create the Element
        el = etree.Element('span')
        el.set('class', 'logika-phonology')

        self.processPhonology(el, data[m.start(0):m.end(0)])
        return el, m.start(0), m.end(0)
    
    def processPhonology(self, parent_element, phon_str):
        part_m = self.PHON_PART.match(phon_str)
        if not part_m:
            return
        if part_m.group(0).strip().startswith('([['):
            paren = etree.SubElement(parent_element, 'span')
            paren.set('class', 'parenthesis')
            self.getFeatureMatrix(paren, part_m.group(3))
        elif part_m.group(0).strip().startswith('[['):
            self.getFeatureMatrix(parent_element, part_m.group(3))
        elif part_m.group(0).strip() == "->":
            arrow = etree.SubElement(parent_element, 'span')
            arrow.set('class', 'phonological-rule-arrow')
            arrow.text = "&xrarr;"
        elif part_m.group(0).strip() == "/":
            slash = etree.SubElement(parent_element, 'span')
            slash.set('class', 'phonological-rule-slash')
            slash.text = "/"
        elif part_m.group(0).strip().startswith("_"):
            underscore = etree.SubElement(parent_element, 'span')
            underscore.set('class', 'phonological-rule-underscore')
            underscore.text = ""

        phon_str = phon_str[part_m.end():]
        if len(phon_str) > 0:
            self.processPhonology(parent_element, phon_str)
        else: 
            return

    def getFeatureMatrix(self, parent_element, features_str):
        features_str = features_str.strip()
        if len(features_str) == 1 or self.IPA_BRACKETS.match(features_str):
            feature = etree.SubElement(parent_element, 'span')
            feature.set('class', 'feature-matrix-char')
            feature.text = features_str
        else:
            features = [f.strip() for f in features_str.split(',')]
            matrix = etree.SubElement(parent_element, 'span')
            matrix.set('class', 'feature-matrix')
            for f in features:
                feature = etree.SubElement(matrix, 'span')
                feature.text = f

class LogikaPhonologyExtension(Extension):
    def extendMarkdown(self, md):
        # Add new patterns        
        PHON_PATTERN = r'(\(?\[\[(.*?)\]\]\)?)(\s*(\(?\[\[(.*?)\]\]\)?)|\s*(->)|\s*(/)|\s*(\_+))*'
        md.inlinePatterns.register(LogikaPhonologyProcessor(PHON_PATTERN, md), 'logika_phonology', 175)

def makeExtension(**kwargs):
    return LogikaPhonologyExtension(**kwargs)