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

import tokenize
from HTMLParser import HTMLParseError
from pyxl.codec.parser import PyxlParser

class PyxlParseError(Exception): pass

def pyxl_tokenize(readline):
    last_nw_token = None
    prev_token = None

    tokens = tokenize.generate_tokens(readline)
    while 1:
        try:
            token = tokens.next()
        except (StopIteration, tokenize.TokenError):
            break

        ttype, tvalue, tstart, tend, tline = token

        if (ttype == tokenize.OP and tvalue == '<' and
            ((last_nw_token[0] == tokenize.OP and last_nw_token[1] == '=') or
             (last_nw_token[0] == tokenize.OP and last_nw_token[1] == '(') or
             (last_nw_token[0] == tokenize.OP and last_nw_token[1] == '[') or
             (last_nw_token[0] == tokenize.OP and last_nw_token[1] == '{') or
             (last_nw_token[0] == tokenize.OP and last_nw_token[1] == ',') or
             (last_nw_token[0] == tokenize.OP and last_nw_token[1] == ':') or
             (last_nw_token[0] == tokenize.NAME and last_nw_token[1] == 'print') or
             (last_nw_token[0] == tokenize.NAME and last_nw_token[1] == 'return'))):
            token = get_pyxl_token(token, tokens)

        if ttype not in (tokenize.INDENT,
                         tokenize.DEDENT,
                         tokenize.NL,
                         tokenize.NEWLINE,
                         tokenize.COMMENT):
            last_nw_token = token

        # tokenize has this bug where when \ is used to continue lines
        # the token row jumps without a newline token being outputted
        # if that happens, we'll yield the \ and the newline for it
        if prev_token:
            prev_ttype, prev_tvalue, prev_tstart, prev_tend, prev_tline = prev_token
            if (prev_tend[0] < tstart[0] and
                prev_ttype not in (tokenize.NEWLINE, tokenize.NL, tokenize.COMMENT)):
                row, col = prev_tend
                yield (tokenize.STRING, '\\', (row, col), (row, col+1), prev_tline)
                yield (tokenize.NL, '\n', (row, col+1), (row, col+2), prev_tline)

        prev_token = token
        yield token

def get_pyxl_token(start_token, tokens):
    ttype, tvalue, tstart, tend, tline = start_token
    pyxl_parser = PyxlParser(tstart[0], tstart[1], tline)
    pyxl_parser.feed(start_token)

    for token in tokens:
        ttype, tvalue, tstart, tend, tline = token

        try:
            pyxl_parser.feed(token)
        except HTMLParseError, html_ex:
            msg = 'HTMLParseError: %s (line:%d: %s)' % (html_ex.msg, tstart[0], tline.strip())
            raise PyxlParseError(msg)
        except AssertionError, assert_ex:
            msg = '%s (line:%d: %s)' % (assert_ex, tstart[0], tline.strip())
            raise PyxlParseError(msg)

        if pyxl_parser.done(): break

    if not pyxl_parser.done():
        lines = ['<%s> at (line:%d: %s)' % (tag, row, line.strip())
                 for tag, row, line in pyxl_parser.openTags]
        raise PyxlParseError('Unclosed Tags: %s' % ', '.join(lines))

    return pyxl_parser.getToken()
