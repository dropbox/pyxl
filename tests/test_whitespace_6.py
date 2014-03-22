# coding: pyxl
from pyxl import html
def test():
    assert str(<frag>
                   {'foo'}
                   <if cond="{True}">
                       {'foo'}
                   </if>
               </frag>) == "foofoo"
