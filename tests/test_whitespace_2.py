# coding: pyxl
from pyxl import html
def test():
    assert str(<div>
                   The owner has not granted you access to this file.
               </div>) == """<div>The owner has not granted you access to this file.</div>"""
