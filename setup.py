#!/usr/bin/env python

import distutils
import os.path

from setuptools import setup
from setuptools.command.install import install as _install

version = "1.0"

PTH = 'import pyxl.codec.register'


class install(_install):
    def initialize_options(self):
        _install.initialize_options(self)
        name = self.distribution.metadata.name

        contents = 'import sys; exec({!r})\n'.format(PTH)
        self.extra_path = (name, contents)

    def finalize_options(self):
        _install.finalize_options(self)

        install_suffix = os.path.relpath(
            self.install_lib, self.install_libbase,
        )
        if install_suffix == '.':
            distutils.log.info('skipping install of .pth during easy-install')
        elif install_suffix == self.extra_path[1]:
            self.install_lib = self.install_libbase
            distutils.log.info(
                "will install .pth to '%s.pth'",
                os.path.join(self.install_lib, self.extra_path[0]),
            )
        else:
            raise AssertionError(
                'unexpected install_suffix',
                self.install_lib, self.install_libbase, install_suffix,
            )


setup(
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
    """,
    cmdclass={'install': install},
)
