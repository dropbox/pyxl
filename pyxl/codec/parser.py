#!/usr/bin/env python

import tokenize
from pyxl import html
from html_tokenizer import (
        HTMLTokenizer,
        ParseError as TokenizerParseError,
        State,
)
from pytokenize import Untokenizer

class ParseError(Exception):
    def __init__(self, message, pos=None):
        if pos is not None:
            super(ParseError, self).__init__("%s at line %d char %d" % ((message,) + pos))
        else:
            super(ParseError, self).__init__(message)

class PyxlParser(HTMLTokenizer):
    def __init__(self, row, col):
        super(PyxlParser, self).__init__()
        self.start = self.end = (row, col)
        self.output = []
        self.open_tags = []
        self.remainder = None
        self.next_thing_is_python = False
        self.last_thing_was_python = False
        self.last_thing_was_close_if_tag = False

    def feed(self, token):
        ttype, tvalue, tstart, tend, tline = token

        assert tstart[0] >= self.end[0], "row went backwards"
        if tstart[0] > self.end[0]:
            self.output.append("\n" * (tstart[0] - self.end[0]))

        # interpret jumps on the same line as a single space
        elif tstart[1] > self.end[1]:
            super(PyxlParser, self).feed(" ")

        self.end = tstart

        if ttype != tokenize.INDENT:
            while tvalue and not self.done():
                c, tvalue = tvalue[0], tvalue[1:]
                if c == "\n":
                    self.end = (self.end[0]+1, 0)
                else:
                    self.end = (self.end[0], self.end[1]+1)
                try:
                    super(PyxlParser, self).feed(c)
                except TokenizerParseError:
                    raise ParseError("HTML Parsing error", self.end)
        if self.done():
            self.remainder = (ttype, tvalue, self.end, tend, tline)
        else:
            self.end = tend

    def feed_python(self, tokens):
        ttype, tvalue, tstart, tend, tline = tokens[0]
        assert tstart[0] >= self.end[0], "row went backwards"
        if tstart[0] > self.end[0]:
            self.output.append("\n" * (tstart[0] - self.end[0]))
        ttype, tvalue, tstart, tend, tline = tokens[-1]
        self.end = tend

        if self.state in [State.DATA, State.CDATA_SECTION]:
            self.next_thing_is_python = True
            self.emit_data()
            self.output.append("%s, " % Untokenizer().untokenize(tokens))
            self.next_thing_is_python = False
            self.last_thing_was_python = True
        elif self.state in [State.BEFORE_ATTRIBUTE_VALUE,
                            State.ATTRIBUTE_VALUE_DOUBLE_QUOTED,
                            State.ATTRIBUTE_VALUE_SINGLE_QUOTED,
                            State.ATTRIBUTE_VALUE_UNQUOTED]:
            super(PyxlParser, self).feed_python(tokens)

    def feed_position_only(self, token):
        """update with any whitespace we might have missed, and advance position to after the
        token"""
        ttype, tvalue, tstart, tend, tline = token
        self.feed((ttype, '', tstart, tstart, tline))
        self.end = tend

    def python_comment_allowed(self):
        """Returns true if we're in a state where a # starts a comment.

        <a # comment before attribute name
           class="bar"# comment after attribute value
           href="#notacomment">
            # comment in data
            Link text
        </a>
        """
        return self.state in (State.DATA, State.TAG_NAME,
                              State.BEFORE_ATTRIBUTE_NAME, State.AFTER_ATTRIBUTE_NAME,
                              State.BEFORE_ATTRIBUTE_VALUE, State.AFTER_ATTRIBUTE_VALUE,
                              State.COMMENT, State.DOCTYPE_CONTENTS, State.CDATA_SECTION)

    def python_mode_allowed(self):
        """Returns true if we're in a state where a { starts python mode.

        <!-- {this isn't python} -->
        """
        return self.state not in (State.COMMENT,)

    def feed_comment(self, token):
        ttype, tvalue, tstart, tend, tline = token
        self.feed((ttype, '', tstart, tstart, tline))
        self.output.append(tvalue)
        self.end = tend

    def get_remainder(self):
        return self.remainder

    def done(self):
        return len(self.open_tags) == 0 and self.state == State.DATA and self.output

    def get_token(self):
        return (tokenize.STRING, ''.join(self.output), self.start, self.end, '')

    @staticmethod
    def safe_attr_name(name):
        if name == "class":
            return "xclass"
        if name == "for":
            return "xfor"
        return name.replace('-', '_').replace(':', 'COLON')

    def _handle_attr_value(self, attr_value):
        def format_parts():
            prev_was_python = False
            for i, part in enumerate(attr_value):
                if type(part) == list:
                    yield part
                    prev_was_python = True
                else:
                    next_is_python = bool(i+1 < len(attr_value) and type(attr_value[i+1]) == list)
                    part = self._normalize_data_whitespace(part, prev_was_python, next_is_python)
                    if part:
                        yield part
                    prev_was_python = False

        attr_value = list(format_parts())
        if len(attr_value) == 1:
            part = attr_value[0]
            if type(part) == list:
                self.output.append(Untokenizer().untokenize(part))
            else:
                self.output.append(repr(part))
        else:
            self.output.append('u"".join((')
            for part in attr_value:
                if type(part) == list:
                    self.output.append('unicode(')
                    self.output.append(Untokenizer().untokenize(part))
                    self.output.append(')')
                else:
                    self.output.append(repr(part))
                self.output.append(', ')
            self.output.append('))')

    @staticmethod
    def _normalize_data_whitespace(data, prev_was_py, next_is_py):
        if not data:
            return ''
        if '\n' in data and not data.strip():
            if prev_was_py and next_is_py:
                return ' '
            else:
                return ''
        if prev_was_py and data.startswith('\n'):
                data = " " + data.lstrip('\n')
        if next_is_py and data.endswith('\n'):
                data = data.rstrip('\n') + " "
        data = data.strip('\n')
        data = data.replace('\r', ' ')
        data = data.replace('\n', ' ')
        return data

    def handle_starttag(self, tag, attrs, call=True):
        self.open_tags.append({'tag':tag, 'row': self.end[0]})
        if tag == 'if':
            if len(attrs) != 1:
                raise ParseError("if tag only takes one attr called 'cond'", self.end)
            if 'cond' not in attrs:
                raise ParseError("if tag must contain the 'cond' attr", self.end)

            self.output.append('html._push_condition(bool(')
            self._handle_attr_value(attrs['cond'])
            self.output.append(')) and html.x_frag()(')
            self.last_thing_was_python = False
            self.last_thing_was_close_if_tag = False
            return
        elif tag == 'else':
            if len(attrs) != 0:
                raise ParseError("else tag takes no attrs", self.end)
            if not self.last_thing_was_close_if_tag:
                raise ParseError("<else> tag must come right after </if>", self.end)

            self.output.append('(not html._last_if_condition) and html.x_frag()(')
            self.last_thing_was_python = False
            self.last_thing_was_close_if_tag = False
            return

        module, dot, identifier = tag.rpartition('.')
        identifier = 'x_%s' % identifier
        x_tag = module + dot + identifier

        if hasattr(html, x_tag):
            self.output.append('html.')
        self.output.append('%s(' % x_tag)

        first_attr = True
        for attr_name, attr_value in attrs.iteritems():
            if first_attr: first_attr = False
            else: self.output.append(', ')

            self.output.append(self.safe_attr_name(attr_name))
            self.output.append('=')
            self._handle_attr_value(attr_value)

        self.output.append(')')
        if call:
            # start call to __call__
            self.output.append('(')
        self.last_thing_was_python = False
        self.last_thing_was_close_if_tag = False

    def handle_endtag(self, tag_name, call=True):
        if call:
            # finish call to __call__
            self.output.append(")")

        assert self.open_tags, "got </%s> but tag stack empty; parsing should be over!" % tag_name

        open_tag = self.open_tags.pop()
        if open_tag['tag'] != tag_name:
            raise ParseError("<%s> on line %d closed by </%s> on line %d" %
                             (open_tag['tag'], open_tag['row'], tag_name, self.end[0]))

        if open_tag['tag'] == 'if':
            self.output.append(',html._leave_if()')
            self.last_thing_was_close_if_tag = True
        else:
            self.last_thing_was_close_if_tag = False

        if len(self.open_tags):
            self.output.append(",")
        self.last_thing_was_python = False

    def handle_startendtag(self, tag_name, attrs):
        self.handle_starttag(tag_name, attrs, call=False)
        self.handle_endtag(tag_name, call=False)

    def handle_data(self, data):
        data = self._normalize_data_whitespace(
                data, self.last_thing_was_python, self.next_thing_is_python)
        if not data:
            return

        # XXX XXX mimics old pyxl, but this is gross and likely wrong. I'm pretty sure we actually
        # want %r instead of this crazy quote substitution and u"%s".
        data = data.replace('"', '\\"')
        self.output.append('html.rawhtml(u"%s"), ' % data)

        self.last_thing_was_python = False
        self.last_thing_was_close_if_tag = False

    def handle_comment(self, data):
        self.handle_startendtag("html_comment", {"comment": [data.strip()]})
        self.last_thing_was_python = False
        self.last_thing_was_close_if_tag = False

    def handle_doctype(self, data):
        self.handle_startendtag("html_decl", {"decl": ['DOCTYPE ' + data]})
        self.last_thing_was_python = False
        self.last_thing_was_close_if_tag = False

    def handle_cdata(self, data):
        self.handle_startendtag("html_marked_decl", {"decl": ['CDATA[' + data]})
        self.last_thing_was_python = False
        self.last_thing_was_close_if_tag = False
