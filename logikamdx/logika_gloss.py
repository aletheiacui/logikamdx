"""
Logika Interlinear Glossing Extension for Python-Markdown
====================================

Copyright 2022 Philologika LLC

License: [BSD](https://opensource.org/licenses/bsd-license.php)


%g% word word word
    gloss gloss gloss
    'translation translation translation.'
"""

from  markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension
import xml.etree.ElementTree as etree
import re

class LogikaGlossProcessor(BlockProcessor):

    RE_ORIGINAL = re.compile('(^\s*\%[Gg]\%)(.+)')

    def __init__(self, parser):
        self.n_words_original = 0
        self.orignal = None
        self.gloss = None
        self.translation = None

        super().__init__(parser)

    def test(self, parent, block):
        '''
        check whether the input has three components:
            original text
            gloss
            translation (optional)
        '''
        rows = [row.strip() for row in block.split('\n')]
        if len(rows) < 2:
            # needs at least rows
            return False
        
        original = rows.pop(0).strip()
        original_match = self.RE_ORIGINAL.match(original)
        if not original_match:
            return False
        
        original = original_match.group(2).strip()
        if len(original) == 0:
            return False

        self.original = original.split()

        gloss = rows.pop(0).strip()
        if len(gloss) == 0:
            return False
        self.gloss = gloss.split()

        if len(rows) == 1:
            translation = rows.pop(0).strip()
            if len(translation) > 0:
                self.translation = translation

        return True


    def run(self, parent, blocks):
        block = blocks.pop(0)
       
        container = etree.SubElement(parent, 'div')
        container.set('class', f'logika-gloss')
        gloss_block = etree.SubElement(container, 'div')
        gloss_block.set('class', 'logika-gloss-block')
        for i, word in enumerate(self.original):
            word_block = etree.SubElement(gloss_block, 'div')
            original_element = etree.SubElement(word_block, 'span')
            original_element.text = word
            gloss_element = etree.SubElement(word_block, 'span')
            original_element.set('class', 'logika-gloss-original')
            gloss_element.set('class', 'logika-gloss-gloss')
            try:
                gloss_element.text = self.gloss[i]
            except IndexError:
                gloss_element.text = 'undefined'
            
        if self.translation:
            translation_element = etree.SubElement(container, 'div')
            translation_element.set('class', f'logika-gloss-translation')
            translation_element.text = self.translation


class LogikaGlossExtension(Extension):
    def extendMarkdown(self, md):
        # Add new patterns        
        md.parser.blockprocessors.register(LogikaGlossProcessor(md.parser), 'logika_gloss', 74)

def makeExtension(**kwargs):
    return LogikaGlossExtension(**kwargs)