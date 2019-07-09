# coding: pyxl
from pyxl import html

def test():
    count = [0]
    def foo(value):
        count[0] += 1
        return value
    assert str(<frag>
                   <if cond="{foo(True)}">a</if>
                   <else>b</else>
                   {<div>lol{10}</div>}
               </frag>) == "a<div>lol10</div>"

    count[0] = 0
    assert str(<frag>
                   <if cond="{foo(False)}">a</if>
                   <else>b</else>
                   # asdf
                   {count[0]} whatever {2}
               </frag>) == "b1 whatever 2"
