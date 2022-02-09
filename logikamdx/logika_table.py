"""
Logika Tables Extension for Python-Markdown
====================================

Modified parsing of tables to Python-Markdown.

Original code Copyright 2009 [Waylan Limberg](http://achinghead.com)

Previous changes Copyright 2008-2014 The Python Markdown Project

Subsequent changes Copyright 2022 Philologika LLC

License: [BSD](https://opensource.org/licenses/bsd-license.php)
"""

from markdown.extensions import Extension
from  markdown.blockprocessors import BlockProcessor
import xml.etree.ElementTree as etree
import re

PIPE_NONE = 0
PIPE_LEFT = 1
PIPE_RIGHT = 2

class LogikaTableProcessor(BlockProcessor):
    """ Process Tables. """

    RE_CODE_PIPES = re.compile(r'(?:(\\\\)|(\\`+)|(`+)|(\\\|)|(\|))')
    RE_END_BORDER = re.compile(r'(?<!\\)(?:\\\\)*\|$')
    RE_BORDER = re.compile(r'(?<!\\)([\=]{5,})(\:\d{1,3})?$')
    RE_TITLE = re.compile(r'(?<!\\)(\:)(.+)(\:)$')
    RE_SEPARATOR = re.compile(r'(?<!\\)(\|?(\={3,})(\:\d{1,3})?(\:\S+)?\|?){2,}')
    RE_SEP_CELL = re.compile(r'(?:\={3,})(\:\d{1,3})?(\:\S+)?')

    def __init__(self, parser):
        self.border = False
        self.separator = None
        self.title = None
        self.caption = None
        self.table_width = "100"
        self.top_border = False
        self.is_table = True
        super().__init__(parser)

    def test(self, parent, block):
        """
        Check for top and bottom borders
        Check for title and caption
        Check the table has at least two columns
        """
        self.border = False
        self.separator = None
        self.title = None
        self.caption = None
        self.table_width = "100"
        self.top_border = False
        self.is_table = True
        
        rows = [row.strip() for row in block.split('\n')]
        # a minimal table should have three rows:
        #   1. a top border or a top separator
        #   2. content
        #   3. bottom border
        if len(rows) < 3:
            return False

        # the top border is either "-------"
        # or separator |---:30|----:30|
        # check top border for width settings
        top_border = rows.pop(0)
        top_match = self.RE_BORDER.match(top_border)
        sep_match = self.RE_SEPARATOR.match(top_border)
        if top_match: 
            if top_match.group(2):
                self.table_width = top_match.group(2).strip(":")
            self.top_border = True
        elif not top_match and sep_match:
            self.border = PIPE_NONE
            if top_border.startswith('|'):
                self.border |= PIPE_LEFT
            if self.RE_END_BORDER.search(top_border) is not None:
                self.border |= PIPE_RIGHT
            self.separator = self._split_row(top_border)
        else:
            return False

        # get bottom border
        bottom_border = rows.pop()
        bottom_match = self.RE_BORDER.match(bottom_border)
        if not bottom_match:
            # missing bottom border
            return False

        # if top and bottom borders have been found
        if (top_match or sep_match) and bottom_match:
            # find title, if exists
            title_match = self.RE_TITLE.match(rows[0])

            if title_match:
                self.title = title_match.group(2)
                # remove title row
                rows = rows[1:]
            
            # find caption, if exists
            caption_match = self.RE_TITLE.match(rows[-1])
            if caption_match:
                self.caption = caption_match.group(2)
                # remove title row
                rows = rows[:-2]

            if not self.separator:
                sep_match = self.RE_SEPARATOR.match(rows[0])
                if not sep_match:
                    return False
                self.border = PIPE_NONE
                if top_border.startswith('|'):
                    self.border |= PIPE_LEFT
                if self.RE_END_BORDER.search(rows[0]) is not None:
                    self.border |= PIPE_RIGHT
                self.separator = self._split_row(rows[0])
                rows = rows[1:]
            
            for row in rows:
                if row.startswith("|") and row.endswith("|"):
                    row = row[1:-1]
                if not "|" in row:
                    self.is_table = False
        return True

    def run(self, parent, blocks):
        # Get default alignment of columns
        block = blocks.pop(0).split('\n')
        rows = [] if len(block) < 3 else block[1:-1]
        if self.top_border:
            rows = rows[1:]
        if self.title:
            rows = rows[1:]
        if self.caption:
            rows = rows[:-2]

        style = []
        for c in self.separator:
            sep_match = self.RE_SEP_CELL.match(c.strip())
            cstyle = ""
            if sep_match.group(1):
                cstyle += f"width:{sep_match.group(1)[1:]}%;"
            if sep_match.group(2):
                cstyle += f"text-align:{sep_match.group(2)[1:]};"
            style.append(cstyle)

        # Build table
        table_div = etree.SubElement(parent, 'div')
        if self.table_width:
            table_div.set('style', f'width:{self.table_width}%')
            table_div.set('class', 'logika-div')

        if self.title:
            title = etree.SubElement(table_div, 'h4')
            title.text = self.title
        if self.is_table:
            table = etree.SubElement(table_div, 'table')
            if len(rows) == 0:
                # Handle empty table
                self._build_empty_row(table, style)
            else:
                for row in rows:
                    self._build_row(row.strip(), table, style)
        else:
            subdiv = etree.SubElement(table_div, 'div')
            subdiv.set("class", "logika-content-div")
            subdiv.text = "\n".join(rows)

        if self.caption:
            caption = etree.SubElement(table_div, 'p')
            caption.text = self.caption
            caption.set("class", "logika-caption")

    def _build_empty_row(self, parent, align):
        """Build an empty row."""
        tr = etree.SubElement(parent, 'tr')
        count = len(align)
        while count:
            etree.SubElement(tr, 'td')
            count -= 1

    def _build_row(self, row, parent, style):
        """ Given a row of text, build table cells. """
        tr = etree.SubElement(parent, 'tr')
        cells = self._split_row(row)
        # We use align here rather than cells to ensure every row
        # contains the same number of columns.
        for i, a in enumerate(style):
            tag = 'td'
            try:
                cell_text = cells[i].strip()
            except IndexError:  # pragma: no cover
                cell_text = ""
            else:
                if cell_text.startswith("!"):
                    tag = "th"
                    cell_text = cell_text[1:]

            c = etree.SubElement(tr, tag)
            c.text = cell_text
            if tag == "td":
                c.set('class', f'table-col-{str(i)}')
            if a:
                c.set('style', style[i])

    def _split_row(self, row):
        """ split a row of text into list of cells. """
        if self.border:
            if row.startswith('|'):
                row = row[1:]
            row = self.RE_END_BORDER.sub('', row)
        return self._split(row)

    def _split(self, row):
        """ split a row of text with some code into a list of cells. """
        elements = []
        pipes = []
        tics = []
        tic_points = []
        tic_region = []
        good_pipes = []

        # Parse row
        # Throw out \\, and \|
        for m in self.RE_CODE_PIPES.finditer(row):
            # Store ` data (len, start_pos, end_pos)
            if m.group(2):
                # \`+
                # Store length of each tic group: subtract \
                tics.append(len(m.group(2)) - 1)
                # Store start of group, end of group, and escape length
                tic_points.append((m.start(2), m.end(2) - 1, 1))
            elif m.group(3):
                # `+
                # Store length of each tic group
                tics.append(len(m.group(3)))
                # Store start of group, end of group, and escape length
                tic_points.append((m.start(3), m.end(3) - 1, 0))
            # Store pipe location
            elif m.group(5):
                pipes.append(m.start(5))

        # Pair up tics according to size if possible
        # Subtract the escape length *only* from the opening.
        # Walk through tic list and see if tic has a close.
        # Store the tic region (start of region, end of region).
        pos = 0
        tic_len = len(tics)
        while pos < tic_len:
            try:
                tic_size = tics[pos] - tic_points[pos][2]
                if tic_size == 0:
                    raise ValueError
                index = tics[pos + 1:].index(tic_size) + 1
                tic_region.append((tic_points[pos][0], tic_points[pos + index][1]))
                pos += index + 1
            except ValueError:
                pos += 1

        # Resolve pipes.  Check if they are within a tic pair region.
        # Walk through pipes comparing them to each region.
        #     - If pipe position is less that a region, it isn't in a region
        #     - If it is within a region, we don't want it, so throw it out
        #     - If we didn't throw it out, it must be a table pipe
        for pipe in pipes:
            throw_out = False
            for region in tic_region:
                if pipe < region[0]:
                    # Pipe is not in a region
                    break
                elif region[0] <= pipe <= region[1]:
                    # Pipe is within a code region.  Throw it out.
                    throw_out = True
                    break
            if not throw_out:
                good_pipes.append(pipe)

        # Split row according to table delimeters.
        pos = 0
        for pipe in good_pipes:
            elements.append(row[pos:pipe])
            pos = pipe + 1
        elements.append(row[pos:])
        return elements

class LogikaTableExtension(Extension):
    """ Add tables to Markdown. """

    def extendMarkdown(self, md):
        """ Add an instance of LogikaTableProcessor to BlockParser. """
        if '|' not in md.ESCAPED_CHARS:
            md.ESCAPED_CHARS.append('|')
        md.parser.blockprocessors.register(LogikaTableProcessor(md.parser), 'logika_table', 75)

def makeExtension(**kwargs): 
    return LogikaTableExtension(**kwargs)