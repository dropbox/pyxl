# coding: pyxl
from pyxl import html

# This weird circumstance could cause extra spaces to get inserted...
def a():
    return <div>
               some stuff
               $'{"#"}'
           </div>
def b():
    return (<div>
                some stuff
                $'{"#"}'
            </div>)

def test():
    assert str(a()) == "<div>some stuff $'#'</div>"
    assert str(b()) == "<div>some stuff $'#'</div>"
