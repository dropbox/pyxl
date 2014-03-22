# coding: pyxl
from pyxl import html
def test():
    assert str(<frag>{<br /> if False else <div></div>}</frag>) == '''<div></div>'''
