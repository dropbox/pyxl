# coding: pyxl
from pyxl import html

def test():
    assert str(<frag>
                   <if cond="{True}">
                       <if cond="{True}">
                           one
                       </if>
                       <else>
                           two
                       </else>
                   </if>
                   <else>
                       <if cond="{True}">
                           three
                       </if>
                       <else>
                           four
                       </else>
                   </else>
               </frag>) == "one"

    assert str(<frag>
                   <if cond="{True}">
                       <if cond="{False}">
                           one
                       </if>
                       <else>
                           two
                       </else>
                   </if>
                   <else>
                       <if cond="{True}">
                           three
                       </if>
                       <else>
                           four
                       </else>
                   </else>
               </frag>) == "two"

    assert str(<frag>
                   <if cond="{False}">
                       <if cond="{False}">
                           one
                       </if>
                       <else>
                           two
                       </else>
                   </if>
                   <else>
                       <if cond="{True}">
                           three
                       </if>
                       <else>
                           four
                       </else>
                   </else>
               </frag>) == "three"

    assert str(<frag>
                   <if cond="{False}">
                       <if cond="{False}">
                           one
                       </if>
                       <else>
                           two
                       </else>
                   </if>
                   <else>
                       <if cond="{False}">
                           three
                       </if>
                       <else>
                           four
                       </else>
                   </else>
               </frag>) == "four"
