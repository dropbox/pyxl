# coding: pyxl
from pyxl import html
unicode = str  # dumb testing hack

def test():
    assert str(<frag><img src="barbaz{'foo'}" /></frag>) == """<img src="barbazfoo" />"""
