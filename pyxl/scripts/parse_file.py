#!/usr/bin/env python

import sys
from pyxl.codec.tokenizer import pyxl_tokenize, pyxl_untokenize

f = open(sys.argv[1], 'r')
print pyxl_untokenize(pyxl_tokenize(f.readline)),
