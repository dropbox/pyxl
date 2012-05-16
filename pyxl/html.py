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

from pyxl.utils import escape
from pyxl.base import x_base

class x_html_element(x_base):
    def to_string(self):
        out = [u'<', self.__tag__]
        for name, value in self.__attributes__.iteritems():
            out.extend((u' ', name, u'="', escape(value), u'"'))
        out.append(u'>')

        for child in self.__children__:
            out.append(x_base.render_child(child))

        out.extend((u'</', self.__tag__, u'>'))
        return u''.join(out)

class x_html_element_nochild(x_base):
    def append(self, child):
        raise Exception('<%s> does not allow children.', self.__tag__)

    def to_string(self):
        out = [u'<', self.__tag__]
        for name, value in self.__attributes__.iteritems():
            out.extend((u' ', name, u'="', escape(value), u'"'))
        out.append(u' />')
        return u''.join(out)

class x_html_comment(x_base):
    __attrs__ = {
        'comment': unicode,
        }

    def to_string(self):
        return '<!--%s-->' % self.attr('comment')

class x_html_decl(x_base):
    __attrs__ = {
        'decl': unicode,
        }

    def to_string(self):
        return '<!%s>' % self.attr('decl')

class x_rawhtml(x_html_element_nochild):
    __attrs__= {
        'text': unicode,
        }

    def to_string(self):
        if type(self.text) != unicode:
            return unicode(self.text, 'utf8')
        return self.text

def rawhtml(text):
    return x_rawhtml(text=text)

class x_frag(x_base):
    def to_string(self):
        return u''.join(self.render_child(c) for c in self.__children__)

class x_a(x_html_element):
    __attrs__ = {
        'href': unicode,
        'rel': unicode,
        'type': unicode,
        'name': unicode,
        'target': unicode,
        }

class x_b(x_html_element):
   pass

class x_body(x_html_element):
   pass

class x_br(x_html_element_nochild):
   pass

class x_button(x_html_element):
    __attrs__ = {
        'accept': unicode,
        'alt': unicode,
        'checked': unicode,
        'disabled': unicode,
        'maxlength': unicode,
        'name': unicode,
        'readonly': unicode,
        'size': unicode,
        'src': unicode,
        'placeholder': unicode,
        'type': unicode,
        'value': unicode,
        'accesskey': unicode,
        }

class x_code(x_html_element):
   pass

class x_div(x_html_element):
   __attrs__ = {
        'contenteditable': unicode,
   }

class x_em(x_html_element):
   pass

class x_embed(x_html_element):
    __attrs__ = {
        'src': unicode,
        'width': unicode,
        'height': unicode,
        'allowscriptaccess': unicode,
        'allowfullscreen': unicode,
        'name': unicode,
        'type': unicode,
    }

class x_form(x_html_element):
    __attrs__ = {
        'action': unicode,
        'method': unicode,
        'enctype': unicode,
        'accept-charset': unicode,
        'accept': unicode,
        'name': unicode,
        'target': unicode,
        'onsubmit': unicode,
        }

class x_frame(x_html_element_nochild):
    __attrs__ = {
        'name': unicode,
        'longdesc': unicode,
        'src': unicode,
        'noresize': unicode,
        'scrolling': unicode,
        'frameborder': unicode,
        }

class x_frameset(x_html_element):
    __attrs__ = {
        'rows': unicode,
        'cols': unicode,
        }

class x_h1(x_html_element):
   pass

class x_h2(x_html_element):
   pass

class x_h3(x_html_element):
   pass

class x_h4(x_html_element):
   pass

class x_h5(x_html_element):
   pass

class x_h6(x_html_element):
   pass

class x_hr(x_html_element):
    pass

class x_head(x_html_element):
    __attrs__ = {
        'profile': unicode,
        'lang': unicode,
        'dir': unicode,
        }

class x_header(x_html_element):
	pass

class x_html(x_html_element):
    __attrs__ = {
        'content': unicode,
        'scheme': unicode,
        'http-equiv': unicode,
        'lang': unicode,
        'dir': unicode,
        'xml:lang': unicode,
        'xmlns': unicode,
        'xmlns:og': unicode,
        'xmlns:fb': unicode,
        }

class x_i(x_html_element):
   pass

class x_iframe(x_html_element):
    __attrs__ = {
        'name': unicode,
        'longdesc': unicode,
        'src': unicode,
        'scrolling': unicode,
        'frameborder': unicode,
        'height': unicode,
        'width': unicode,
        'marginheight': unicode,
        'marginwidth': unicode,
        }

class x_img(x_html_element_nochild):
    __attrs__ = {
        'src': unicode,
        'alt': unicode,
        'height': unicode,
        'width': unicode,
        'longdesc': unicode,
        'ismap': unicode,
        'onload': unicode,
        }

class x_input(x_html_element_nochild):
    __attrs__ = {
        'accept': unicode,
        'alt': unicode,
        'checked': unicode,
        'disabled': unicode,
        'maxlength': unicode,
        'validate-max-length': unicode,  # used for javascript validation
        'name': unicode,
        'readonly': unicode,
        'size': unicode,
        'src': unicode,
        'placeholder': unicode,
        'z-index': unicode,
        'autocomplete': unicode,
        'autocorrect': unicode,
        'type': unicode,
        'value': unicode,
        'accesskey': unicode,
        'tabindex': unicode,
        'required': unicode,
        }


class x_label(x_html_element):
    __attrs__ = {
        'for': unicode,
        'accesskey': unicode,
        }

class x_li(x_html_element):
   pass

class x_link(x_html_element_nochild):
    __attrs__ = {
        'charset': unicode,
        'href': unicode,
        'hreflang': unicode,
        'media': unicode,
        'rel': unicode,
        'rev': unicode,
        'target': unicode,
        'type': unicode,
        }

class x_meta(x_html_element_nochild):
    __attrs__ = {
        'http-equiv': unicode,
        'name': unicode,
        'property': unicode,
        'content': unicode,
        "scheme": unicode,
        }

class x_noframes(x_html_element):
   pass

class x_noscript(x_html_element):
   pass

class x_object(x_html_element):
    __attrs__ = {
        'align': unicode,
        'archive': unicode,
        'border': unicode,
        'classid': unicode,
        'codebase': unicode,
        'codetype': unicode,
        'data': unicode,
        'declare': unicode,
        'height': unicode,
        'hspace': unicode,
        'name': unicode,
        'standby': unicode,
        'type': unicode,
        'usemap': unicode,
        'vspace': unicode,
        'width': unicode,
        }

class x_ol(x_html_element):
   pass

class x_option(x_html_element):
    __attrs__ = {
        'disabled': unicode,
        'label': unicode,
        'selected': unicode,
        'value': unicode,
        }

class x_p(x_html_element):
   pass

class x_pre(x_html_element):
   pass

class x_script(x_html_element):
    __attrs__ = {
        'type': unicode,
        'charset': unicode,
        'defer': unicode,
        'src': unicode,
        }

class x_section(x_html_element):
	pass

class x_select(x_html_element):
    __attrs__ = {
        'disabled': unicode,
        'multiple': unicode,
        'name': unicode,
        'size': unicode,
        'tabindex': unicode,
        'required': unicode,
        }

class x_span(x_html_element):
   pass

class x_strong(x_html_element):
   pass

class x_style(x_html_element):
    __attrs__ = {
        'type': unicode,
        'media': unicode,
        }

class x_table(x_html_element):
    __attrs__ = {
        'border': unicode,
        'cellpadding': unicode,
        'cellspacing': unicode,
        'frame': unicode,
        'rules': unicode,
        'summary': unicode,
        'width': unicode,
        }

class x_td(x_html_element):
    __attrs__ = {
        'abbr': unicode,
        'align': unicode,
        'axis': unicode,
        'char': unicode,
        'charoff': unicode,
        'colspan': unicode,
        'headers': unicode,
        'rowspan': unicode,
        'scope': unicode,
        'valign': unicode,
        'width': unicode,
        }

class x_th(x_html_element):
    __attrs__ = {
        'abbr': unicode,
        'align': unicode,
        'axis': unicode,
        'char': unicode,
        'charoff': unicode,
        'colspan': unicode,
        'headers': unicode,
        'rowspan': unicode,
        'scope': unicode,
        'valign': unicode,
        }

class x_tr(x_html_element):
    __attrs__ = {
        'abbr': unicode,
        'align': unicode,
        'axis': unicode,
        'char': unicode,
        'charoff': unicode,
        'colspan': unicode,
        'headers': unicode,
        'rowspan': unicode,
        'scope': unicode,
        'valign': unicode,
        }

class x_textarea(x_html_element):
    __attrs__ = {
        'cols': unicode,
        'rows': unicode,
        'disabled': unicode,
        'placeholder': unicode,
        'name': unicode,
        'readonly': unicode,
        'autocorrect': unicode,
        'autocomplete': unicode,
        'autocapitalize': unicode,
        'spellcheck': unicode,
        'tabindex': unicode,
        }

class x_title(x_html_element):
   pass

class x_tr(x_html_element):
    __attrs__ = {
        'align': unicode,
        'char': unicode,
        'charoff': unicode,
        'valign': unicode,
        }

class x_tbody(x_html_element):
    pass

class x_thead(x_html_element):
    pass

class x_u(x_html_element):
    pass

class x_ul(x_html_element):
    __attrs__ = {
        'onload': unicode,
        }
    pass

class x_canvas(x_html_element):
    __attrs__ = {
        'width': unicode,
        'height': unicode,
    }
    pass
