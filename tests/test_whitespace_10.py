# coding: pyxl
from pyxl import html
def test():
    assert str(<div class="{'foo'} {'bar'}"></div>) == '<div class="foo bar"></div>'
