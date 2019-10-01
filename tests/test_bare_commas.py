# coding: pyxl
from pyxl import html

def test():
    title = "hi"
    x, y, z = 1, 2, 3
    assert str(
        <div>
            {title}
            {x, y, z}
        </div>
    ) == "<div>hi 123</div>"
