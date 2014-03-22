# coding: pyxl
from pyxl import html
def test():
    assert str(<frag>{<br /> if True else <div></div>}</frag>) == '''<br />'''
