#!/usr/bin/env python

import distutils.core
import sys

version = "1.0"

distutils.core.setup(
    name="pyxl",
    version=version,
    packages = ["pyxl", "pyxl.codec", "pyxl.scripts", "pyxl.examples"],
    author="Akhil Wable",
    author_email="akhil.wable@gmail.com",
    url="http://github.com/awable/pyxl",
    download_url="http://github.com/downloads/awable/pyxl/pyxl-%s.tar.gz" % version,
    license="http://www.apache.org/licenses/LICENSE-2.0",
    description="""
        Pyxl is an open source package that extends Python to support inline HTML. It converts
        HTML fragments into valid Python expressions, and is meant as a replacement for traditional
        python templating systems like Mako or Cheetah. It automatically escapes data, enforces
        correct markup and makes it easier to write reusable and well structured UI code.
        Pyxl was inspired by the XHP project at Facebook.
    """
)
