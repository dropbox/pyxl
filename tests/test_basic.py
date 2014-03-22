# coding: pyxl
import unittest2
from pyxl import html

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

if __name__ == '__main__':
    unittest2.main()
