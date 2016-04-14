# coding: pyxl
import unittest2
from pyxl import html
from pyxl.base import PyxlException, x_base
from pyxl.element import x_element

class PyxlTests(unittest2.TestCase):

    def test_basics(self):
        self.assertEqual(<div />.to_string(), '<div></div>')
        self.assertEqual(<img src="blah" />.to_string(), '<img src="blah" />')
        self.assertEqual(<div class="c"></div>.to_string(), '<div class="c"></div>')
        self.assertEqual(<div><span></span></div>.to_string(), '<div><span></span></div>')
        self.assertEqual(<frag><span /><span /></frag>.to_string(), '<span></span><span></span>')

    def test_escaping(self):
        self.assertEqual(<div class="&">&{'&'}</div>.to_string(), '<div class="&amp;">&&amp;</div>')
        self.assertEqual(<div>{html.rawhtml('&')}</div>.to_string(), '<div>&</div>')

    def test_comments(self):
        pyxl = (
            <div
                class="blah" # attr comment
                >  # comment1
                <!-- comment2 -->
                text# comment3
                # comment4
            </div>)
        self.assertEqual(pyxl.to_string(), '<div class="blah">text</div>')

    def test_cond_comment(self):
        s = 'blahblah'
        self.assertEqual(
            <cond_comment cond="lt IE 8"><div class=">">{s}</div></cond_comment>.to_string(),
            '<!--[if lt IE 8]><div class="&gt;">blahblah</div><![endif]-->')
        self.assertEqual(
            <cond_comment cond="(lt IE 8) & (gt IE 5)"><div>{s}</div></cond_comment>.to_string(),
            '<!--[if (lt IE 8) & (gt IE 5)]><div>blahblah</div><![endif]-->')

    def test_decl(self):
        self.assertEqual(
            <script><![CDATA[<div><div>]]></script>.to_string(),
            '<script><![CDATA[<div><div>]]></script>')

    def test_form_error(self):
        self.assertEqual(
            <form_error name="foo" />.to_string(),
            '<form:error name="foo" />')

    def test_default_attrs(self):
        class x_foo(x_element):
            __attrs__ = {
                'value': (int, 5),
            }

            def render(self):
                return <div>{self.value}</div>

        self.assertEqual(<foo />.to_string(), '<div>5</div>')
        self.assertEqual(<foo />.value, 5)

        foo = <foo value=2 />
        self.assertEqual(foo.value, 2)

        foo.set_attr('value', 10)
        self.assertEqual(foo.value, 10)
        self.assertEqual(foo.to_string(), '<div>10</div>')

        with self.assertRaises(AssertionError):
            class x_bar(x_base):
                __attrs__ = {
                    'value': (str, 10),
                }

    def test_enum_attrs(self):
        class x_foo(x_base):
            __attrs__ = {
                'value': ['a', 'b'],
            }

            def _to_list(self, l):
                pass

        self.assertEqual(<foo />.attr('value'), 'a')
        self.assertEqual(<foo />.value, 'a')
        self.assertEqual(<foo value="b" />.attr('value'), 'b')
        self.assertEqual(<foo value="b" />.value, 'b')
        with self.assertRaises(PyxlException):
            <foo value="c" />

        class x_bar(x_base):
            __attrs__ = {
                'value': ['a', None, 'b'],
            }

            def _to_list(self, l):
                pass

        with self.assertRaises(PyxlException):
            <bar />.attr('value')

        with self.assertRaises(PyxlException):
            <bar />.value

        class x_baz(x_base):
            __attrs__ = {
                'value': [None, 'a', 'b'],
            }

            def _to_list(self, l):
                pass

        self.assertEqual(<baz />.value, None)

if __name__ == '__main__':
    unittest2.main()
