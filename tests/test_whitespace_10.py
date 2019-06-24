# coding: pyxl
from pyxl import html
unicode = str  # dumb testing hack

def test():
    assert str(<div class="{'foo'} {'bar'}"></div>) == '<div class="foo bar"></div>'
