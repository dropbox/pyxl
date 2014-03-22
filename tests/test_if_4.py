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
                   {count[0]}
               </frag>) == "a1"

    count[0] = 0
    assert str(<frag>
                   <if cond="{foo(False)}">a</if>
                   <else>b</else>
                   {count[0]}
               </frag>) == "b1"
