# coding: pyxl
from pyxl import html


def test():
    assert (
        str(
            (
                <div>
                {
                    # test
                    0
                }
                </div>
            )
        )
        == "<div>0</div>"
    )
