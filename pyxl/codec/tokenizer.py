from . import pytokenize as tokenize
import re
from io import StringIO
from pyxl.codec.parser import PyxlParser
from .pytokenize import Untokenizer
import ast
from collections import namedtuple

Pos = namedtuple('Pos', ['row', 'col'])
Token = namedtuple('Token', ['ttype', 'value', 'start', 'end', 'line'])


def fix_token(t):
    ttype, value, start, end, line = t
    return Token(ttype, value, Pos(*start), Pos(*end), line)


class PyxlUnfinished(Exception): pass


class PyxlParseError(Exception): pass


def get_end_pos(start_pos, tvalue):
    row, col = start_pos
    for c in tvalue:
        if c == '\n':
            col = 0
            row += 1
        else:
            col += 1
    return Pos(row, col)


class RewindableTokenStream(object):
    """
    A token stream, with the ability to rewind and restart tokenization while maintaining correct
    token position information.

    Invariants:
        - zero_row and zero_col are the correct values to adjust the line and possibly column of the
        tokens being produced by _tokens.
        - Tokens in unshift_buffer have locations with absolute position (relative to the beginning
          of the file, not relative to where we last restarted tokenization).
    """

    def __init__(self, readline):
        self.orig_readline = readline
        self.unshift_buffer = []
        self.rewound_buffer = None
        self._tokens = tokenize.generate_tokens(self._readline)
        self.zero_row, self.zero_col = (0, 0)
        self.stop_readline = False

    def _dumpstate(self):
        print("tokenizer state:")
        print("  zero:", (self.zero_row, self.zero_col))
        print("  rewound_buffer:", self.rewound_buffer)
        print("  unshift_buffer:", self.unshift_buffer)

    def _readline(self):
        if self.stop_readline:
            return ""
        if self.rewound_buffer:
            line = self.rewound_buffer.readline()
            if line:
                return line
            else:
                self.rewound_buffer = None  # fallthrough to orig_readline
        return self.orig_readline()

    def _flush(self):
        self.stop_readline = True
        tokens = list(tok for tok in self)
        self.stop_readline = False
        return tokens

    def _adjust_position(self, pos):
        row, col = pos
        if row == 1:  # rows are 1-indexed
            col += self.zero_col
        row += self.zero_row
        return Pos(row, col)

    def rewind_and_retokenize(self, rewind_token):
        """Rewind the given token (which is expected to be the last token read from this stream, or
        the end of such token); then restart tokenization."""
        ttype, tvalue, (row, col), tend, tline = rewind_token
        tokens = [rewind_token] + self._flush()
        self.zero_row, self.zero_col = (row - 1, col)  # rows are 1-indexed, cols are 0-indexed
        self.rewound_buffer = StringIO(Untokenizer().untokenize(tokens))
        self.unshift_buffer = []
        self._tokens = tokenize.generate_tokens(self._readline)

    def __next__(self):
        if self.unshift_buffer:
            token = self.unshift_buffer.pop(0)
        else:
            ttype, tvalue, tstart, tend, tline = next(self._tokens)
            tstart = self._adjust_position(tstart)
            tend = self._adjust_position(tend)
            token = Token(ttype, tvalue, tstart, tend, tline)
        return token

    def __iter__(self):
        return self

    def unshift(self, token):
        """Rewind the given token, without retokenizing. It will be the next token read from the
        stream."""
        self.unshift_buffer[:0] = [token]


def untokenize(toks):
    return Untokenizer().untokenize(toks).lstrip().rstrip(' ')


def untokenize_with_column(tokens):
    """Untokenize a series of tokens, with it in its proper column.

    This requires inserting a newline before it.
    """
    tok_type, token, start, end, line = tokens[0]
    return Untokenizer(start[0] - 1, 0).untokenize(tokens)


def pyxl_untokenize(tokens):
    return Untokenizer(1, 0).untokenize(tokens)


def pyxl_tokenize(readline, invertible=False):
    return cleanup_tokens(transform_tokens(RewindableTokenStream(readline), invertible))


def pyxl_invert_tokenize(readline):
    return cleanup_tokens(invert_tokens(RewindableTokenStream(readline)))


def cleanup_tokens(tokens):
    for token in tokens:
        ttype, tvalue, tstart, tend, tline = token

        # strip trailing newline from non newline tokens
        if tvalue and tvalue[-1] == '\n' and ttype not in (tokenize.NL, tokenize.NEWLINE):
            ltoken = list(token)
            ltoken[1] = tvalue[:-1]
            token = Token(*ltoken)

        yield token


def transform_tokens(tokens, invertible):
    last_nw_token = None
    prev_token = None

    curly_depth = 0

    while 1:
        try:
            token = next(tokens)
        except (StopIteration, tokenize.TokenError):
            break

        ttype, tvalue, tstart, tend, tline = token

        if ttype == tokenize.OP and tvalue == '{':
            curly_depth += 1
        if ttype == tokenize.OP and tvalue == '}':
            curly_depth -= 1
            if curly_depth < 0:
                tokens.unshift(token)
                return

        if (ttype == tokenize.OP and tvalue == '<' and
            (last_nw_token == None or # if we have *just* entered python mode e.g
             (last_nw_token[0] == tokenize.OP and last_nw_token[1] == '=') or
             (last_nw_token[0] == tokenize.OP and last_nw_token[1] == '(') or
             (last_nw_token[0] == tokenize.OP and last_nw_token[1] == '[') or
             (last_nw_token[0] == tokenize.OP and last_nw_token[1] == '{') or
             (last_nw_token[0] == tokenize.OP and last_nw_token[1] == ',') or
             (last_nw_token[0] == tokenize.OP and last_nw_token[1] == ':') or
             (last_nw_token[0] == tokenize.NAME and last_nw_token[1] == 'print') or
             (last_nw_token[0] == tokenize.NAME and last_nw_token[1] == 'else') or
             (last_nw_token[0] == tokenize.NAME and last_nw_token[1] == 'yield') or
             (last_nw_token[0] == tokenize.NAME and last_nw_token[1] == 'return'))):
            token = get_pyxl_token(token, tokens, invertible)

        if ttype not in (tokenize.INDENT,
                         tokenize.DEDENT,
                         tokenize.NL,
                         tokenize.NEWLINE,
                         tokenize.COMMENT):
            last_nw_token = token

        prev_token = token
        yield token


def sanitize_token(token):
    """Escape brackets in a token that is going to be put in a format string"""
    if '{' in token.value or '}' in token.value:
        return Token(token.ttype, token.value.replace("{", "{{").replace("}", "}}"),
                     token.start, token.end, token.line)
    else:
        return token


def get_pyxl_token(start_token, tokens, invertible):
    ttype, tvalue, tstart, tend, tline = start_token
    pyxl_parser = PyxlParser(tstart.row, tstart.col)
    pyxl_parser.feed(start_token)

    if invertible:
        # In invertible mode, keep track of all the tokens we see in pyxl and
        # each python fragment that appears
        pyxl_tokens = [start_token]
        python_fragments = []

    for token in tokens:
        ttype, tvalue, tstart, tend, tline = token

        if tvalue and tvalue[0] == '{':
            if pyxl_parser.python_mode_allowed():
                # We've hit a python fragment
                initial_tstart = tstart

                mid, right = tvalue[0], tvalue[1:]
                division = get_end_pos(tstart, mid)
                pyxl_parser.feed_position_only(Token(ttype, mid, tstart, division, tline))
                tokens.rewind_and_retokenize(Token(ttype, right, division, tend, tline))
                python_tokens = list(transform_tokens(tokens, invertible))

                close_curly = next(tokens)
                ttype, tvalue, tstart, tend, tline = close_curly
                close_curly_sub = Token(ttype, '', tend, tend, tline)

                # strip comments in the invertible version
                pyxl_parser.feed_python(
                    (strip_comments(python_tokens) if invertible else python_tokens)
                    + [close_curly_sub])

                if invertible:
                    # If we are doing invertible generation, put in a format placeholder
                    # into the collected pyxl tokens and collect python fragment separately.

                    # We keep each fragment wrapped in the curlies it came in (because just
                    # relying on the commas) doesn't work when there are undelimited commas.
                    # This also serves to preserve any internal whitespace in the fragment so
                    # it can be restored later.
                    open_curly = Token(ttype, '{', initial_tstart, division, tline)

                    pyxl_tokens.append(Token(ttype, '{}', initial_tstart, tend, ''))

                    python_fragments.append(
                        [open_curly] + python_tokens + [close_curly])

                continue
            # else fallthrough to pyxl_parser.feed(token)
        elif tvalue and ttype == tokenize.COMMENT:
            if not pyxl_parser.python_comment_allowed():
                tvalue, rest = tvalue[0], tvalue[1:]
                division = get_end_pos(tstart, tvalue)
                tokens.unshift(Token(tokenize.ERRORTOKEN, rest, division, tend, tline))
                token = Token(ttype, tvalue, tstart, division, tline)
                # fallthrough to pyxl_parser.feed(token)
            else:
                # strip comments in the invertible version
                if not invertible:
                    pyxl_parser.feed_comment(token)
                if invertible:
                    pyxl_tokens.append(sanitize_token(token))
                continue
        elif tvalue and tvalue[0] == '#':
            # let the python tokenizer grab the whole comment token
            tokens.rewind_and_retokenize(token)
            continue
        else:
            sp = re.split('([#{])', tvalue, maxsplit=1)
            if len(sp) > 1:
                tvalue, mid, right = sp
                division = get_end_pos(tstart, tvalue)
                tokens.unshift(Token(ttype, mid+right, division, tend, tline))
                token = Token(ttype, tvalue, tstart, division, tline)
                # fallthrough to pyxl_parser.feed(token)

        pyxl_parser.feed(token)
        if invertible:
            pyxl_tokens.append(sanitize_token(token))

        if pyxl_parser.done(): break

    if not pyxl_parser.done():
        lines = ['<%s> at (line:%d)' % (tag_info['tag'], tag_info['row'])
                 for tag_info in pyxl_parser.open_tags]
        raise PyxlParseError('Unclosed Tags: %s' % ', '.join(lines))

    remainder = pyxl_parser.get_remainder()
    if remainder:
        remainder = fix_token(remainder)
        tokens.rewind_and_retokenize(remainder)
        # Strip the remainder out from the last seen token
        if invertible and remainder.value:
            assert '{' not in remainder.value and '}' not in remainder.value
            last = pyxl_tokens[-1]
            pyxl_tokens[-1] = Token(
                last.ttype, last.value[:-len(remainder[1])],
                last.start, remainder.start, last.line)

    pyxl_parser_start = Pos(*pyxl_parser.start)
    if invertible:
        output = "html.PYXL('''{}''', {}, {}, {}{}{})".format(
            untokenize(pyxl_tokens).replace('\\', '\\\\').replace("'", "\\'"),
            # Include the real compiled pyxl so that tools can see all the gritty details
            untokenize([pyxl_parser.get_token()]),
            # Include the start column so we can shift it if needed
            pyxl_parser_start.col,
            # Include the columns of each python fragment so we can shift them if needed
            ''.join([str(first_non_ws_token(x).start.col) + ', ' for x in python_fragments]),
            # When untokenizing python fragments, make sure to place them in their
            # proper columns so that we don't detect a shift if there wasn't one.
            ''.join([untokenize_with_column(x) + ', ' for x in python_fragments]),
            # Stick a final argument at the end so that all the real arguments are
            # always terminated by commas (and don't pick up spurious whitespace
            # with certain black formatting modes)
            '0',
        )
        return Token(tokenize.STRING, output, pyxl_parser_start, Pos(*pyxl_parser.end), '')
    else:
        return fix_token(pyxl_parser.get_token())


def try_fixing_indent(s, diff, align_to=None, first_lines=0):
    """Given a string, try to fix its internal indentation"""
    if diff == 0 or '\n' not in s:
        return s
    lines = s.split('\n')
    if len(lines) < 2:
        return s

    internal_diff = 0
    # If we are making a change, and we have an align_to specified,
    # shift lines so that the last line is aligned with the first.
    if align_to is not None:
        wo_space = lines[-1].lstrip(" ")
        leading_spaces = len(lines[-1]) - len(wo_space)
        if wo_space and wo_space[0] == '<':
            internal_diff = align_to - leading_spaces

    fixed = [lines[0]]
    early_spacing = " " * abs(diff), diff
    late_spacing =  " " * abs(diff + internal_diff), diff + internal_diff
    for i, line in enumerate(lines[1:]):
        spacing, cdiff = late_spacing if i + 1 >= first_lines else early_spacing

        if cdiff > 0 and line:
            line = spacing + line
        elif cdiff < 0 and line.startswith(spacing):
            line = line[len(spacing):]
        fixed.append(line)

    return '\n'.join(fixed)


def first_non_ws_token(tokens):
    for token in tokens:
        if token.ttype not in (tokenize.INDENT,
                               tokenize.DEDENT,
                               tokenize.NL,
                               tokenize.NEWLINE):
            return token
    # well... let's return *something*
    return tokens[0]


def strip_comments(tokens):
    return [tok for tok in tokens if tok.ttype != tokenize.COMMENT]


def invert_tokens(tokens):
    saved_tokens = []

    curly_depth = 0

    in_pyxl = []
    start_depth = []
    arg_buffers_stack = []
    current_buffer_stack = []

    while 1:
        try:
            token = next(tokens)
        except (StopIteration, tokenize.TokenError):
            if in_pyxl:
                raise PyxlUnfinished
            break

        ttype, tvalue, tstart, tend, tline = token

        if ttype == tokenize.NAME and tvalue == 'html' and len(saved_tokens) == 0:
            saved_tokens.append(token)
            continue
        elif ttype == tokenize.OP and tvalue == '.' and len(saved_tokens) == 1:
            saved_tokens.append(token)
            continue
        elif ttype == tokenize.NAME and tvalue == 'PYXL' and len(saved_tokens) == 2:
            saved_tokens.append(token)
            continue
        if ttype == tokenize.OP and tvalue == '(' and len(saved_tokens) == 3:
            start_depth.append(curly_depth)
            curly_depth += 1
            in_pyxl.append(saved_tokens[0].start)
            saved_tokens = []
            current_buffer_stack.append([])
            arg_buffers_stack.append([])

            continue
        else:
            if in_pyxl:
                current_buffer_stack[-1].extend(saved_tokens)
            else:
                yield from saved_tokens
            saved_tokens = []

        if ttype == tokenize.OP and tvalue in '{([':
            curly_depth += 1
        if ttype == tokenize.OP and tvalue in '})]':
            curly_depth -= 1
            if in_pyxl and curly_depth == start_depth[-1]:
                pyxl_start = in_pyxl.pop()
                arg_buffers = arg_buffers_stack.pop()
                if current_buffer_stack[-1]:
                    arg_buffers.append(current_buffer_stack[-1])
                current_buffer_stack.pop()
                start_depth.pop()

                fmt_buffer, _, start_pos_buffer, *pos_and_arg_buffers, dummy_zero = arg_buffers

                num_args = len(pos_and_arg_buffers)//2
                orig_pos_buffers = pos_and_arg_buffers[:num_args]
                real_arg_buffers = pos_and_arg_buffers[num_args:]

                orig_poses = [int(untokenize(strip_comments(x))) for x in orig_pos_buffers]
                real_poses = [first_non_ws_token(strip_comments(x)).start.col
                              for x in real_arg_buffers] # grab the columns...
                fmt = ast.literal_eval(untokenize(strip_comments(fmt_buffer)))
                orig_start_col = int(untokenize(strip_comments(start_pos_buffer)))

                # If the pyxl literal has been moved off the line with html.PYXL
                # has newlines in it, and we are not inside any nesting structures,
                # reparenthesize it and push it onto a newline.
                # This produces much better looking code.
                initial_tok = None
                pyxl_literal_start = first_non_ws_token(fmt_buffer).start

                if curly_depth == 0 and pyxl_start.row != pyxl_literal_start.row and '\n' in fmt:
                    reparenthesize = True
                    new_start = pyxl_literal_start
                else:
                    reparenthesize = False
                    new_start = pyxl_start

                # Shift the indentation position of all of the arguments to the columns
                # they were at in the original source. (The final pyxl literal will then
                # be shifted from its original column to its new column.)
                diff = new_start[1] - orig_start_col
                args = [try_fixing_indent(untokenize(buf), orig_pos - real_pos)
                        for buf, orig_pos, real_pos
                        in zip(real_arg_buffers, orig_poses, real_poses)]

                # format to get the raw pyxl
                raw_pyxl = fmt.format(*args)
                # count the number of lines produced by the *first* line of the format
                # string, since we skip aligning those with the final
                first_lines = fmt.split('\n')[0].format(*args).count('\n') + 1
                # and then try to repair its internal indentation if the start position shifted
                fixed_pyxl = try_fixing_indent(raw_pyxl, new_start[1] - orig_start_col,
                                               align_to=orig_start_col, first_lines=first_lines)

                if reparenthesize:
                    # Insert parentheses back around the formatted pyxl
                    # We need to futz with tokens some to do this
                    pyxl_literal_end = fmt_buffer[-1].end
                    if pyxl_literal_end.row < token.start.row - 1:
                        pyxl_literal_end = Pos(token.start.row - 1, pyxl_literal_end.col)
                    out_tokens = [
                        Token(tokenize.OP, '(', pyxl_start, pyxl_start, ''),
                        Token(tokenize.STRING, fixed_pyxl, pyxl_literal_start, pyxl_literal_end, ''),
                        token,
                    ]
                else:
                    out_tokens = [Token(tokenize.STRING, fixed_pyxl, new_start, tend, '')]

                if in_pyxl:
                    current_buffer_stack[-1].extend(out_tokens)
                else:
                    yield from out_tokens
                continue
            if curly_depth < 0:
                tokens.unshift(token)
                return

        if (in_pyxl and ttype == tokenize.OP and tvalue == ','
                and curly_depth == start_depth[-1] + 1):
            arg_buffers_stack[-1].append(current_buffer_stack[-1])
            current_buffer_stack[-1] = []
            continue
        elif in_pyxl:
            current_buffer_stack[-1].append(token)
            continue

        prev_token = token
        yield token
