#!/usr/bin/env python
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import re, tokenize
from HTMLParser import HTMLParser

class PyxlParser(HTMLParser):

    def __init__(self, row, col, line):
        self.buffer = []
        self.startPos = (row, col)
        self.lastPos = self.startPos
        self.collectedData = ''
        self.row = row
        self.col = col
        self.line = line
        self.openTags = []
        HTMLParser.__init__(self)

    def feed(self, token):
        ttype, tvalue, tstart, tend, tline = token
        self.line = tline

        # Handle whitespace
        (prev_row, prev_col) = self.lastPos
        (cur_row, cur_col) = tstart
        (end_row, end_col) = tend

        assert cur_row >= prev_row, "Unexpected jump in row"
        self.lastPos = (end_row, end_col)

        # are we now on a new line?
        if cur_row > prev_row:
            self._appendRows(cur_row - prev_row)

        # are we on a muliline statement?
        if end_row > cur_row:
            self._appendRows(end_row - cur_row)

        # interpret jumps on the same line as a single space
        if cur_row == prev_row and cur_col > prev_col:
            HTMLParser.feed(self, ' ')

        HTMLParser.feed(self, tvalue)

    def done(self):
        return not len(self.openTags) and not self.rawdata

    def getToken(self):
        endPos = (self.row, self.col)
        return (tokenize.STRING, ''.join(self.buffer), self.startPos, endPos, None)

    def _appendRows(self, num_rows):
        self.row += num_rows
        self._appendString('\n' * num_rows)
        self.col = 0

    def _appendString(self, string):
        self.buffer.append(string)
        self.col += len(string)

    def _handle_starttag(self, tag, attrs):
        self._handle_enddata()

        if tag == 'if':
            assert len(attrs) == 1, "if tag only takes one attr called 'cond'"
            assert attrs[0][0] == 'cond', "if tag must contain the 'cond' attr"

            self._appendString('bool(')
            self._handle_attr_value(attrs[0][1])
            self._appendString(') and x_frag()')
            return

        self._appendString('x_%s(' % tag)

        first_attr = True
        for attr_name, attr_value in attrs:
            if first_attr: first_attr = False
            else: self._appendString(', ')

            self._appendString(PyxlParser._safeAttrName(attr_name))
            self._appendString('=')
            self._handle_attr_value(attr_value)

        self._appendString(')')

    def _handle_attr_value(self, attr_value):
        if attr_value and attr_value[0] == '{':
            assert attr_value[-1] == '}', "Expecting } got %s" % attr_value[-1]
            self._appendString(attr_value[1:-1])
        else:
            attr_value = attr_value.replace('"', '\\"')
            self._appendString('"".join(map(unicode, (')
            self._handle_text_and_code(attr_value, is_attr_value=True)
            self._appendString(')))')

    @staticmethod
    def _safeAttrName(name):
        if name == 'class':
            return 'xclass'
        if name == 'for':
            return 'xfor'
        return name.replace('-', '_').replace(':', 'COLON')

    def handle_startendtag(self, tag, attrs):
        self._handle_starttag(tag, attrs)
        if not len(self.openTags): return
        self._appendString(',')

    def handle_starttag(self, tag, attrs):
        self._handle_starttag(tag, attrs)
        self._appendString('(')
        self.openTags.append((tag, self.row, self.line))

    def handle_endtag(self, tag):
        self._handle_enddata()
        close_tag, row, line = self.openTags.pop()
        assert close_tag == tag, "'%s' closed with '%s'" % (close_tag, tag)

        self._appendString(')')
        if not len(self.openTags): return
        self._appendString(',')

    def handle_data(self, data):
        self.collectedData += data

    def handle_entityref(self, name):
        self.collectedData += '&%s;' % name

    def handle_charref(self, name):
        self.collectedData += '&#%s' % name

    whitespaceRe = re.compile(ur"[\s]+", re.U)
    def _handle_enddata(self):

         # empty multiline data will be ignored
        if (not self.collectedData or
            ('\n' in self.collectedData and not self.collectedData.strip())):
            self.collectedData = ''
            return

        self._handle_text_and_code(self.collectedData)
        self.collectedData = ''

    TEXT_AND_CODE_RE = re.compile('((?<!\\\\){.*?(?<!\\\\)})', re.S)
    def _handle_text_and_code(self, data, is_attr_value=False):
        parts = [part for part in self.TEXT_AND_CODE_RE.split(data) if part]

        for part in parts:
            is_python = part[0] == '{'
            part = part.replace('\}', '}')
            part = part.replace('\{', '{')

            if is_python:
                part = part.replace('\n', ' ')
                part = part.replace('\r', ' ')
                self._appendString(part[1:-1])
                self._appendString(', ')
            elif part.strip('\n'):
                # escape newlines
                part = part.strip('\n')
                part = part.replace('\n', '\\n')
                part = part.replace('\r', '\\r')
                part = part.replace('"', '\\"')
                if not is_attr_value:
                    self._appendString('rawhtml(')
                self._appendString('u"')
                self._appendString(part)
                self._appendString('"')
                if not is_attr_value:
                    self._appendString(')')
                self._appendString(', ')
