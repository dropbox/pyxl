# coding: pyxl
import pytest

from pyxl import html
from pyxl.base import PyxlException, x_base

def test_basics():
    assert str(<div />) == '<div></div>'
    assert str(<img src="blah" />) == '<img src="blah" />'
    assert str(<div class="c"></div>) == '<div class="c"></div>'
    assert str(<div><span></span></div>) == '<div><span></span></div>'
    assert str(<frag><span /><span /></frag>) == '<span></span><span></span>'

def test_escaping():
    assert str(<div class="&">&{'&'}</div>) == '<div class="&amp;">&&amp;</div>'
    assert str(<div>{html.rawhtml('&')}</div>) == '<div>&</div>'

def test_comments():
    pyxl = (
        <div
            class="blah" # attr comment
            >  # comment1
            <!-- comment2 -->
            text# comment3
            # comment4
        </div>)
    assert str(pyxl) == '<div class="blah">text</div>'

def test_cond_comment():
    s = 'blahblah'
    assert (str(<cond_comment cond="lt IE 8"><div class=">">{s}</div></cond_comment>)
        == '<!--[if lt IE 8]><div class="&gt;">blahblah</div><![endif]-->')
    assert (str(<cond_comment cond="(lt IE 8) & (gt IE 5)"><div>{s}</div></cond_comment>)
        == '<!--[if (lt IE 8) & (gt IE 5)]><div>blahblah</div><![endif]-->')

def test_decl():
    assert (str(<script><![CDATA[<div><div>]]></script>)
        == '<script><![CDATA[<div><div>]]></script>')

def test_form_error():
    assert str(<form_error name="foo" />) == '<form:error name="foo" />'

def test_enum_attrs():
    class x_foo(x_base):
        __attrs__ = {
            'value': ['a', 'b'],
        }

        def _to_list(self, l):
            pass

    assert (<foo />.attr('value')) == 'a'
    assert (<foo />.value) == 'a'
    assert (<foo value="b" />.attr('value')) == 'b'
    assert (<foo value="b" />.value) == 'b'

    with pytest.raises(PyxlException):
        <foo value="c" />

    class x_bar(x_base):
        __attrs__ = {
            'value': ['a', None, 'b'],
        }

        def _to_list(self, l):
            pass

    with pytest.raises(PyxlException):
        <bar />.attr('value')

    with pytest.raises(PyxlException):
        <bar />.value

    class x_baz(x_base):
        __attrs__ = {
            'value': [None, 'a', 'b'],
        }

        def _to_list(self, l):
            pass

    assert (<baz />.value) == None
