# coding: pyxl
from pyxl import html
def test():
    assert str(<span>
                   <div>Test</div>\
               </span>) == "<span><div>Test</div></span>"
