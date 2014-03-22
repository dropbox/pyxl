"""
A naive but strict HTML tokenizer. Based directly on
http://www.w3.org/TR/2011/WD-html5-20110525/tokenization.html

In the ATTRIBUTE_VALUE and BEFORE_ATTRIBUTE_VALUE states, python tokens are accepted.
"""

import sys
from collections import OrderedDict

class State(object):
    DATA = 1
    # unused states: charrefs, RCDATA, script, RAWTEXT, PLAINTEXT
    TAG_OPEN = 7
    END_TAG_OPEN = 8
    TAG_NAME = 9
    # unused states: RCDATA, RAWTEXT, script
    BEFORE_ATTRIBUTE_NAME = 34
    ATTRIBUTE_NAME = 35
    AFTER_ATTRIBUTE_NAME = 36
    BEFORE_ATTRIBUTE_VALUE = 37
    ATTRIBUTE_VALUE_DOUBLE_QUOTED = 38
    ATTRIBUTE_VALUE_SINGLE_QUOTED = 39
    ATTRIBUTE_VALUE_UNQUOTED = 40
    # unused state: CHARREF_IN_ATTRIBUTE_VALUE = 41
    AFTER_ATTRIBUTE_VALUE = 42
    SELF_CLOSING_START_TAG = 43
    # unused state: BOGUS_COMMENT_STATE = 44
    MARKUP_DECLARATION_OPEN = 45
    COMMENT_START = 46
    COMMENT_START_DASH = 47
    COMMENT = 48
    COMMENT_END_DASH = 49
    COMMENT_END = 50
    # unused state: COMMENT_END_BANG = 51
    DOCTYPE = 52
    DOCTYPE_CONTENTS = 53 # Gross oversimplification. Not to spec.
    # unused states: doctypes
    CDATA_SECTION = 68

    @classmethod
    def state_name(cls, state_val):
        for k, v in cls.__dict__.iteritems():
            if v == state_val:
                return k
        assert False, "impossible state value %r!" % state_val

class Tag(object):
    def __init__(self):
        self.tag_name = None
        self.attrs = OrderedDict()
        self.endtag = False
        self.startendtag = False

class ParseError(Exception):
    pass

class BadCharError(Exception):
    def __init__(self, state, char):
        super(BadCharError, self).__init__("unexpected character %r in state %r" %
                                           (char, State.state_name(state)))

class Unimplemented(Exception):
    pass

class HTMLTokenizer(object):

    def __init__(self):
        self.state = State.DATA

        # attribute_value is a list, where each element is either a string or a list of python
        # tokens.

        self.data = ""
        self.tag = None
        self.tag_name = None
        self.attribute_name = None
        self.attribute_value = None
        self.markup_declaration_buffer = None

    def handle_data(self, data):
        assert False, "subclass should override"

    def handle_starttag(self, tag_name, attrs):
        assert False, "subclass should override"

    def handle_startendtag(self, tag_name, attrs):
        assert False, "subclass should override"

    def handle_endtag(self, tag_name):
        assert False, "subclass should override"

    def handle_comment(self, tag_name):
        assert False, "subclass should override"

    def handle_doctype(self, data):
        assert False, "subclass should override"

    def handle_cdata(self, tag_name):
        assert False, "subclass should override"

    def emit_data(self):
        self.handle_data(self.data)
        self.data = ""

    def emit_tag(self):
        if self.tag.startendtag and self.tag.endtag:
            raise ParseError("both startendtag and endtag!?")
        if self.tag.startendtag:
            self.handle_startendtag(self.tag.tag_name, self.tag.attrs)
        elif self.tag.endtag:
            self.handle_endtag(self.tag.tag_name)
        else:
            self.handle_starttag(self.tag.tag_name, self.tag.attrs)

    def emit_comment(self):
        self.handle_comment(self.data)
        self.data = ""

    def emit_doctype(self):
        self.handle_doctype(self.data)
        self.data = ""

    def emit_cdata(self):
        self.handle_cdata(self.data)
        self.data = ""

    def got_attribute(self):
        if self.attribute_name in self.tag.attrs:
            raise ParseError("repeat attribute name %r" % self.attribute_name)
        self.tag.attrs[self.attribute_name] = self.attribute_value
        self.attribute_name = None
        self.attribute_value = None

    def add_data_char(self, build, c):
        """ For adding a new character to e.g. an attribute value """
        if len(build) and type(build[-1]) == str:
            build[-1] += c
        else:
            build.append(c)

    def feed(self, c):
        if self.state == State.DATA:
            if c == '<':
                self.emit_data()
                self.state = State.TAG_OPEN
            # Pass through; it's the browser's problem to understand these.
            #elif c == '&':
            #    raise Unimplemented
            else:
                self.data += c

        elif self.state == State.TAG_OPEN:
            self.tag = Tag()
            if c == '!':
                self.markup_declaration_buffer = ""
                self.state = State.MARKUP_DECLARATION_OPEN
            elif c == '/':
                self.state = State.END_TAG_OPEN
            elif c.isalpha():
                self.tag.tag_name = c
                self.state = State.TAG_NAME
            else:
                raise BadCharError(self.state, c)

        elif self.state == State.END_TAG_OPEN:
            self.tag.endtag = True
            if c.isalpha():
                self.tag.tag_name = c
                self.state = State.TAG_NAME
            else:
                raise BadCharError(self.state, c)

        elif self.state == State.TAG_NAME:
            if c in '\t\n\f ':
                self.state = State.BEFORE_ATTRIBUTE_NAME
            elif c == '/':
                self.state = State.SELF_CLOSING_START_TAG
            elif c == '>':
                self.emit_tag()
                self.state = State.DATA
            else:
                self.tag.tag_name += c

        elif self.state == State.BEFORE_ATTRIBUTE_NAME:
            if c in '\t\n\f ':
                pass
            elif c == '/':
                self.state = State.SELF_CLOSING_START_TAG
            elif c == '>':
                self.emit_tag()
                self.state = State.DATA
            elif c in "\"'<=":
                raise BadCharError(self.state, c)
            else:
                self.attribute_name = c.lower()
                self.state = State.ATTRIBUTE_NAME

        elif self.state == State.ATTRIBUTE_NAME:
            if c in '\t\n\f ':
                self.state = State.AFTER_ATTRIBUTE_NAME
            elif c == '/':
                self.got_attribute()
                self.state = State.SELF_CLOSING_START_TAG
            elif c == '=':
                self.state = State.BEFORE_ATTRIBUTE_VALUE
            elif c == '>':
                self.emit_tag()
                self.state = State.DATA
            elif c in "\"'<":
                raise BadCharError(self.state, c)
            else:
                self.attribute_name += c.lower()

        elif self.state == State.AFTER_ATTRIBUTE_NAME:
            if c in '\t\n\f ':
                pass
            elif c == '/':
                self.got_attribute()
                self.state = State.SELF_CLOSING_START_TAG
            elif c == '=':
                self.state = State.BEFORE_ATTRIBUTE_VALUE
            elif c == '>':
                self.got_attribute()
                self.emit_tag()
                self.state = State.DATA
            elif c in "\"'<":
                raise BadCharError(self.state, c)

        elif self.state == State.BEFORE_ATTRIBUTE_VALUE:
            if c in '\t\n\f ':
                pass
            elif c == '"':
                self.attribute_value = []
                self.state = State.ATTRIBUTE_VALUE_DOUBLE_QUOTED
            elif c == '&':
                self.attribute_value = []
                self.state = State.ATTRIBUTE_VALUE_UNQUOTED
                self.feed(c) # rehandle c
            elif c == "'":
                self.attribute_value = []
                self.state = State.ATTRIBUTE_VALUE_SINGLE_QUOTED
            elif c in '><=`':
                raise BadCharError(self.state, c)
            else:
                self.attribute_value = [c]
                self.state = State.ATTRIBUTE_VALUE_UNQUOTED

        elif self.state == State.ATTRIBUTE_VALUE_DOUBLE_QUOTED:
            if c == '"':
                self.state = State.AFTER_ATTRIBUTE_VALUE
            # Pass through; it's the browser's problem to understand these.
            #elif c == '&':
            #    raise Unimplemented
            else:
                self.add_data_char(self.attribute_value, c)

        elif self.state == State.ATTRIBUTE_VALUE_SINGLE_QUOTED:
            if c == "'":
                self.state = State.AFTER_ATTRIBUTE_VALUE
            # Pass through; it's the browser's problem to understand these.
            #elif c == '&':
            #    raise Unimplemented
            else:
                self.add_data_char(self.attribute_value, c)

        elif self.state == State.ATTRIBUTE_VALUE_UNQUOTED:
            if c in '\t\n\f ':
                self.got_attribute()
                self.state = State.BEFORE_ATTRIBUTE_NAME
            elif c == '>':
                self.got_attribute()
                self.emit_tag()
                self.state = State.DATA
            elif c in "\"'<=`":
                raise BadCharError(self.state, c)
            # Pass through; it's the browser's problem to understand these.
            #elif c == '&':
            #    raise Unimplemented
            else:
                self.add_data_char(self.attribute_value, c)

        elif self.state == State.AFTER_ATTRIBUTE_VALUE:
            self.got_attribute()
            if c in '\t\n\f ':
                self.state = State.BEFORE_ATTRIBUTE_NAME
            elif c == '/':
                self.state = State.SELF_CLOSING_START_TAG
            elif c == '>':
                self.emit_tag()
                self.state = State.DATA
            else:
                raise BadCharError(self.state, c)

        elif self.state == State.SELF_CLOSING_START_TAG:
            self.tag.startendtag = True
            if c == '>':
                self.emit_tag()
                self.state = State.DATA
            else:
                raise BadCharError(self.state, c)

        elif self.state == State.MARKUP_DECLARATION_OPEN:
            self.markup_declaration_buffer += c
            if self.markup_declaration_buffer == "--":
                self.data = ""
                self.state = State.COMMENT_START
            elif self.markup_declaration_buffer.lower() == "DOCTYPE".lower():
                self.state = State.DOCTYPE
            elif self.markup_declaration_buffer == "[CDATA[":
                self.data = ""
                self.cdata_buffer = ""
                self.state = State.CDATA_SECTION
            elif not ("--".startswith(self.markup_declaration_buffer) or
                      "DOCTYPE".lower().startswith(self.markup_declaration_buffer.lower()) or
                      "[CDATA[".startswith(self.markup_declaration_buffer)):
                raise BadCharError(self.state, c)

        elif self.state == State.COMMENT_START:
            if c == "-":
                self.state = State.COMMENT_START_DASH
            elif c == ">":
                raise BadCharError(self.state, c)
            else:
                self.data += c
                self.state = State.COMMENT

        elif self.state == State.COMMENT_START_DASH:
            if c == "-":
                self.state = State.COMMENT_END
            elif c == ">":
                raise BadCharError(self.state, c)
            else:
                self.data += "-" + c
                self.state = State.COMMENT

        elif self.state == State.COMMENT:
            if c == "-":
                self.state = State.COMMENT_END_DASH
            else:
                self.data += c

        elif self.state == State.COMMENT_END_DASH:
            if c == "-":
                self.state = State.COMMENT_END
            else:
                self.data += "-" + c
                self.state = State.COMMENT

        elif self.state == State.COMMENT_END:
            if c == ">":
                self.emit_comment()
                self.state = State.DATA
            else:
                raise BadCharError(self.state, c)

        elif self.state == State.DOCTYPE:
            if c in "\t\n\f ":
                self.data = ""
                self.state = State.DOCTYPE_CONTENTS
            else:
                raise BadCharError(self.state, c)

        elif self.state == State.DOCTYPE_CONTENTS:
            if c == ">":
                self.emit_doctype()
                self.state = State.DATA
            else:
                self.data += c

        elif self.state == State.CDATA_SECTION:
            self.cdata_buffer += c
            if self.cdata_buffer == "]]>":
                self.emit_cdata()
                self.state = State.DATA
            else:
                while self.cdata_buffer and not "]]>".startswith(self.cdata_buffer):
                    self.data += self.cdata_buffer[0]
                    self.cdata_buffer = self.cdata_buffer[1:]

        else:
            assert False, "bad state! %r" % self.state

    def feed_python(self, tokens):
        if self.state == State.BEFORE_ATTRIBUTE_VALUE:
            self.attribute_value = [tokens]
            self.state = State.ATTRIBUTE_VALUE_UNQUOTED
        elif self.state in [State.ATTRIBUTE_VALUE_DOUBLE_QUOTED,
                            State.ATTRIBUTE_VALUE_SINGLE_QUOTED,
                            State.ATTRIBUTE_VALUE_UNQUOTED]:
            self.attribute_value.append(tokens)
        else:
            raise ParseError("python not allow in state %r" % State.state_name(self.state))

class HTMLTokenDumper(HTMLTokenizer):
    def handle_data(self, data):
        print "DATA %r" % data

    def handle_starttag(self, tag_name, attrs):
        print "STARTTAG %r %r" % (tag_name, attrs)

    def handle_startendtag(self, tag_name, attrs):
        print "STARTENDTAG %r %r" % (tag_name, attrs)

    def handle_endtag(self, tag_name):
        print "ENDTAG %r" % tag_name

def main(filename):
    dumper = HTMLTokenDumper()
    with open(filename) as f:
        for line in f:
            for c in line:
                dumper.feed(c)

if __name__ == "__main__":
    main(*sys.argv[1:])
