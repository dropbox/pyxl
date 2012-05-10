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

import __builtin__
import codecs, cStringIO, encodings, tokenize
import traceback
from encodings import utf_8
from pyxl import html
from pyxl import utils
from pyxl.codec.tokenizer import pyxl_tokenize

class PyxlStreamReader(utf_8.StreamReader):
    def __init__(self, *args, **kwargs):
        codecs.StreamReader.__init__(self, *args, **kwargs)

        try:
            data = tokenize.untokenize(pyxl_tokenize(self.stream.readline))
        except Exception, ex:
            print ex
            raise

        self.stream = cStringIO.StringIO(data)

def search_function(encoding):
    if encoding != 'pyxl': return None
    # Assume utf8 encoding
    utf8=encodings.search_function('utf8')
    return codecs.CodecInfo(
        name = 'pyxl',
        encode = utf8.encode,
        decode = utf8.decode,
        incrementalencoder = utf8.incrementalencoder,
        incrementaldecoder = utf8.incrementaldecoder,
        streamreader = PyxlStreamReader,
        streamwriter = utf8.streamwriter)

codecs.register(search_function)

__builtin__.rawhtml = utils.rawhtml
__builtin__.x_html_comment = html.x_html_comment
__builtin__.x_html_decl = html.x_html_decl
__builtin__.x_frag = html.x_frag
__builtin__.x_a = html.x_a
__builtin__.x_b = html.x_b
__builtin__.x_body = html.x_body
__builtin__.x_br = html.x_br
__builtin__.x_button = html.x_button
__builtin__.x_code = html.x_code
__builtin__.x_div = html.x_div
__builtin__.x_em = html.x_em
__builtin__.x_embed = html.x_embed
__builtin__.x_form = html.x_form
__builtin__.x_frame = html.x_frame
__builtin__.x_frameset = html.x_frameset
__builtin__.x_h1 = html.x_h1
__builtin__.x_h2 = html.x_h2
__builtin__.x_h3 = html.x_h3
__builtin__.x_h4 = html.x_h4
__builtin__.x_h5 = html.x_h5
__builtin__.x_h6 = html.x_h6
__builtin__.x_hr = html.x_hr
__builtin__.x_head = html.x_head
__builtin__.x_header = html.x_header
__builtin__.x_html = html.x_html
__builtin__.x_i = html.x_i
__builtin__.x_iframe = html.x_iframe
__builtin__.x_img = html.x_img
__builtin__.x_input = html.x_input
__builtin__.x_label = html.x_label
__builtin__.x_li = html.x_li
__builtin__.x_link = html.x_link
__builtin__.x_meta = html.x_meta
__builtin__.x_noframes = html.x_noframes
__builtin__.x_noscript = html.x_noscript
__builtin__.x_object = html.x_object
__builtin__.x_ol = html.x_ol
__builtin__.x_option = html.x_option
__builtin__.x_p = html.x_p
__builtin__.x_pre = html.x_pre
__builtin__.x_script = html.x_script
__builtin__.x_section = html.x_section
__builtin__.x_select = html.x_select
__builtin__.x_span = html.x_span
__builtin__.x_strong = html.x_strong
__builtin__.x_style = html.x_style
__builtin__.x_table = html.x_table
__builtin__.x_td = html.x_td
__builtin__.x_th = html.x_th
__builtin__.x_tr = html.x_tr
__builtin__.x_textarea = html.x_textarea
__builtin__.x_title = html.x_title
__builtin__.x_tr = html.x_tr
__builtin__.x_tbody = html.x_tbody
__builtin__.x_thead = html.x_thead
__builtin__.x_u = html.x_u
__builtin__.x_ul = html.x_ul
__builtin__.x_canvas = html.x_canvas
