#!/usr/bin/env python

from pyxl.utils import escape
from pyxl.base import x_base

# for backwards compatibility.
from pyxl.browser_hacks import x_cond_comment

_if_condition_stack = []
_last_if_condition = None

def _push_condition(cond):
    _if_condition_stack.append(cond)
    return cond

def _leave_if():
    global _last_if_condition
    _last_if_condition = _if_condition_stack.pop()
    return []

class x_html_element(x_base):
    def _to_list(self, l):
        l.extend(('<', self.__tag__))
        for name, value in self.__attributes__.items():
            l.extend((' ', name, '="', escape(value), '"'))
        l.append('>')

        for child in self.__children__:
            x_base._render_child_to_list(child, l)

        l.extend(('</', self.__tag__, '>'))

class x_html_element_nochild(x_base):
    def append(self, child):
        raise Exception('<%s> does not allow children.', self.__tag__)

    def _to_list(self, l):
        l.extend(('<', self.__tag__))
        for name, value in self.__attributes__.items():
            l.extend((' ', name, '="', escape(value), '"'))
        l.append(' />')

class x_html_comment(x_base):
    __attrs__ = {
        'comment': str,
        }

    def _to_list(self, l):
        pass

class x_html_decl(x_base):
    __attrs__ = {
        'decl': str,
        }

    def _to_list(self, l):
        l.extend(('<!', self.attr('decl'), '>'))

class x_html_marked_decl(x_base):
    __attrs__ = {
        'decl': str,
        }

    def _to_list(self, l):
        l.extend(('<![', self.attr('decl'), ']]>'))

class x_html_ms_decl(x_base):
    __attrs__ = {
        'decl': str,
        }

    def _to_list(self, l):
        l.extend(('<![', self.attr('decl'), ']>'))

class x_rawhtml(x_html_element_nochild):
    __attrs__= {
        'text': str,
        }

    def _to_list(self, l):
        if not isinstance(self.text, str):
            l.append(str(self.text, 'utf8'))
        else:
            l.append(self.text)

def rawhtml(text):
    return x_rawhtml(text=text)

class x_frag(x_base):
    def _to_list(self, l):
        for child in self.__children__:
            self._render_child_to_list(child, l)

class x_a(x_html_element):
    __attrs__ = {
        'href': str,
        'rel': str,
        'type': str,
        'name': str,
        'target': str,
        'download': str,
        }

class x_abbr(x_html_element):
    pass

class x_acronym(x_html_element):
    pass

class x_address(x_html_element):
    pass

class x_area(x_html_element_nochild):
    __attrs__ = {
        'alt': str,
        'coords': str,
        'href': str,
        'nohref': str,
        'target': str,
        }

class x_article(x_html_element):
    pass

class x_aside(x_html_element):
    pass

class x_audio(x_html_element):
    __attrs__ = {
        'src': str
        }

class x_b(x_html_element):
   pass

class x_big(x_html_element):
   pass

class x_blockquote(x_html_element):
    __attrs__ = {
        'cite': str,
        }

class x_body(x_html_element):
    __attrs__ = {
        'contenteditable': str,
        }

class x_br(x_html_element_nochild):
   pass

class x_button(x_html_element):
    __attrs__ = {
        'disabled': str,
        'name': str,
        'type': str,
        'value': str,
        }

class x_canvas(x_html_element):
    __attrs__ = {
        'height': str,
        'width': str,
        }

class x_caption(x_html_element):
   pass

class x_cite(x_html_element):
   pass

class x_code(x_html_element):
   pass

class x_col(x_html_element_nochild):
    __attrs__ = {
        'align': str,
        'char': str,
        'charoff': int,
        'span': int,
        'valign': str,
        'width': str,
        }

class x_colgroup(x_html_element):
    __attrs__ = {
        'align': str,
        'char': str,
        'charoff': int,
        'span': int,
        'valign': str,
        'width': str,
        }

class x_datalist(x_html_element):
    pass

class x_dd(x_html_element):
   pass

class x_del(x_html_element):
    __attrs__ = {
        'cite': str,
        'datetime': str,
        }

class x_div(x_html_element):
   __attrs__ = {
        'contenteditable': str,
       }

class x_dfn(x_html_element):
   pass

class x_dl(x_html_element):
   pass

class x_dt(x_html_element):
   pass

class x_em(x_html_element):
   pass

class x_embed(x_html_element):
    __attrs__ = {
        'src': str,
        'width': str,
        'height': str,
        'allowscriptaccess': str,
        'allowfullscreen': str,
        'name': str,
        'type': str,
        }

class x_figure(x_html_element):
   pass

class x_figcaption(x_html_element):
   pass

class x_fieldset(x_html_element):
   pass

class x_footer(x_html_element):
    pass

class x_form(x_html_element):
    __attrs__ = {
        'action': str,
        'accept': str,
        'accept-charset': str,
        'autocomplete': str,
        'enctype': str,
        'method': str,
        'name': str,
        'novalidate': str,
        'target': str,
        }

class x_form_error(x_base):
    __attrs__ = {
        'name': str
        }

    def _to_list(self, l):
        l.extend(('<form:error name="', self.attr('name'), '" />'))

class x_frame(x_html_element_nochild):
    __attrs__ = {
        'frameborder': str,
        'longdesc': str,
        'marginheight': str,
        'marginwidth': str,
        'name': str,
        'noresize': str,
        'scrolling': str,
        'src': str,
        }

class x_frameset(x_html_element):
    __attrs__ = {
        'rows': str,
        'cols': str,
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

class x_head(x_html_element):
    __attrs__ = {
        'profile': str,
        }

class x_header(x_html_element):
    pass

class x_hr(x_html_element_nochild):
    pass

class x_html(x_html_element):
    __attrs__ = {
        'content': str,
        'scheme': str,
        'http-equiv': str,
        'xmlns': str,
        'xmlns:og': str,
        'xmlns:fb': str,
        }

class x_i(x_html_element):
   pass

class x_iframe(x_html_element):
    __attrs__ = {
        'frameborder': str,
        'height': str,
        'longdesc': str,
        'marginheight': str,
        'marginwidth': str,
        'name': str,
        'sandbox': str,
        'scrolling': str,
        'src': str,
        'width': str,
        # rk: 'allowTransparency' is not in W3C's HTML spec, but it's supported in most modern browsers.
        'allowtransparency': str,
        'allowfullscreen': str,
        }

class x_video(x_html_element):
    __attrs__ = {
        'autoplay': str,
        'controls': str,
        'height': str,
        'loop': str,
        'muted': str,
        'poster': str,
        'preload': str,
        'src': str,
        'width': str,
        }

class x_img(x_html_element_nochild):
    __attrs__ = {
        'alt': str,
        'src': str,
        'height': str,
        'ismap': str,
        'longdesc': str,
        'usemap': str,
        'vspace': str,
        'width': str,
        }

class x_input(x_html_element_nochild):
    __attrs__ = {
        'accept': str,
        'align': str,
        'alt': str,
        'autofocus': str,
        'checked': str,
        'disabled': str,
        'list': str,
        'max': str,
        'maxlength': str,
        'min': str,
        'name': str,
        'pattern': str,
        'placeholder': str,
        'readonly': str,
        'size': str,
        'src': str,
        'step': str,
        'type': str,
        'value': str,
        'autocomplete': str,
        'autocorrect': str,
        'required': str,
        'spellcheck': str,
        'multiple': str,
        }

class x_ins(x_html_element):
    __attrs__ = {
        'cite': str,
        'datetime': str,
        }

class x_kbd(x_html_element):
    pass

class x_label(x_html_element):
    __attrs__ = {
        'for': str,
        }

class x_legend(x_html_element):
   pass

class x_li(x_html_element):
   pass

class x_link(x_html_element_nochild):
    __attrs__ = {
        'charset': str,
        'href': str,
        'hreflang': str,
        'media': str,
        'rel': str,
        'rev': str,
        'sizes': str,
        'target': str,
        'type': str,
        }

class x_main(x_html_element):
    # we are not enforcing the w3 spec of one and only one main element on the
    # page
    __attrs__ = {
        'role': str,
    }

class x_map(x_html_element):
    __attrs__ = {
        'name': str,
        }

class x_meta(x_html_element_nochild):
    __attrs__ = {
        'content': str,
        'http-equiv': str,
        'name': str,
        'property': str,
        'scheme': str,
        'charset': str,
        }

class x_nav(x_html_element):
    pass

class x_noframes(x_html_element):
   pass

class x_noscript(x_html_element):
   pass

class x_object(x_html_element):
    __attrs__ = {
        'align': str,
        'archive': str,
        'border': str,
        'classid': str,
        'codebase': str,
        'codetype': str,
        'data': str,
        'declare': str,
        'height': str,
        'hspace': str,
        'name': str,
        'standby': str,
        'type': str,
        'usemap': str,
        'vspace': str,
        'width': str,
        }

class x_ol(x_html_element):
   pass

class x_optgroup(x_html_element):
    __attrs__ = {
        'disabled': str,
        'label': str,
        }

class x_option(x_html_element):
    __attrs__ = {
        'disabled': str,
        'label': str,
        'selected': str,
        'value': str,
        }

class x_p(x_html_element):
   pass

class x_param(x_html_element):
    __attrs__ = {
        'name': str,
        'type': str,
        'value': str,
        'valuetype': str,
        }

class x_pre(x_html_element):
   pass

class x_progress(x_html_element):
    __attrs__ = {
        'max': int,
        'value': int,
    }

class x_q(x_html_element):
    __attrs__ = {
        'cite': str,
        }

class x_samp(x_html_element):
   pass

class x_script(x_html_element):
    __attrs__ = {
        'async': str,
        'charset': str,
        'defer': str,
        'src': str,
        'type': str,
        }

class x_section(x_html_element):
    pass

class x_select(x_html_element):
    __attrs__ = {
        'disabled': str,
        'multiple': str,
        'name': str,
        'size': str,
        'required': str,
        }

class x_small(x_html_element):
   pass

class x_span(x_html_element):
   pass

class x_strong(x_html_element):
   pass

class x_style(x_html_element):
    __attrs__ = {
        'media': str,
        'type': str,
        }

class x_sub(x_html_element):
   pass

class x_sup(x_html_element):
   pass

class x_table(x_html_element):
    __attrs__ = {
        'border': str,
        'cellpadding': str,
        'cellspacing': str,
        'frame': str,
        'rules': str,
        'summary': str,
        'width': str,
        }

class x_tbody(x_html_element):
    __attrs__ = {
        'align': str,
        'char': str,
        'charoff': str,
        'valign': str,
        }

class x_td(x_html_element):
    __attrs__ = {
        'abbr': str,
        'align': str,
        'axis': str,
        'char': str,
        'charoff': str,
        'colspan': str,
        'headers': str,
        'rowspan': str,
        'scope': str,
        'valign': str,
        }

class x_textarea(x_html_element):
    __attrs__ = {
        'cols': str,
        'rows': str,
        'disabled': str,
        'placeholder': str,
        'name': str,
        'readonly': str,
        'autocorrect': str,
        'autocomplete': str,
        'autocapitalize': str,
        'spellcheck': str,
        'autofocus': str,
        'required': str,
        }

class x_tfoot(x_html_element):
    __attrs__ = {
        'align': str,
        'char': str,
        'charoff': str,
        'valign': str,
        }

class x_th(x_html_element):
    __attrs__ = {
        'abbr': str,
        'align': str,
        'axis': str,
        'char': str,
        'charoff': str,
        'colspan': str,
        'rowspan': str,
        'scope': str,
        'valign': str,
        }

class x_thead(x_html_element):
    __attrs__ = {
        'align': str,
        'char': str,
        'charoff': str,
        'valign': str,
        }

class x_time(x_html_element):
    __attrs__ = {
        'datetime': str,
        }

class x_title(x_html_element):
   pass

class x_tr(x_html_element):
    __attrs__ = {
        'align': str,
        'char': str,
        'charoff': str,
        'valign': str,
        }

class x_tt(x_html_element):
    pass

class x_u(x_html_element):
    pass

class x_ul(x_html_element):
    pass

class x_var(x_html_element):
    pass
