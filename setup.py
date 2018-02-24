#!/usr/bin/env python

import distutils.core
import sys

version = "1.0"

distutils.core.setup(
    name="pyxl3",
    version=version,
    packages = ["pyxl", "pyxl.codec", "pyxl.scripts"],
    url="http://github.com/gvanrossum/pyxl3",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    description="""
        This is a Python 3 port of the original pyxl package.
        It is used to support the original pyxl version
        (still in use at Dropbox) in mypy (which is Python 3).
    """
)
