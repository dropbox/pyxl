# coding: pyxl
from pyxl import html
def test():
    assert str(<frag>{'<div class="foo"> foobar </div>'}</frag>) == """&lt;div class=&quot;foo&quot;&gt; foobar &lt;/div&gt;"""
