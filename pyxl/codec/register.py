#!/usr/bin/env python
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import codecs, cStringIO, encodings, tokenize
import traceback
from encodings import utf_8
from pyxl.codec.tokenizer import pyxl_tokenize

def pyxl_transform(stream):
    try:
        output = tokenize.untokenize(pyxl_tokenize(stream.readline))
    except Exception, ex:
        print ex
        raise

    return output

def pyxl_decode(input, errors='strict'):
    stream = cStringIO.StringIO(input)
    return utf_8.decode(pyxl_transform(stream), errors)

class PyxlIncrementalDecoder(utf_8.IncrementalDecoder):
    def decode(self, input, final=False):
        self.buffer += input
        if final:
            stream = cStringIO.StringIO(self.buffer)
            self.buffer = ''
            return super(PyxlIncrementalDecoder, self).decode(pyxl_transform(stream), final=True)

class PyxlStreamReader(utf_8.StreamReader):
    def __init__(self, *args, **kwargs):
        codecs.StreamReader.__init__(self, *args, **kwargs)
        self.stream = cStringIO.StringIO(pyxl_transform(self.stream))

def search_function(encoding):
    if encoding != 'pyxl': return None
    # Assume utf8 encoding
    utf8=encodings.search_function('utf8')
    return codecs.CodecInfo(
        name = 'pyxl',
        encode = utf8.encode,
        decode = pyxl_decode,
        incrementalencoder = utf8.incrementalencoder,
        incrementaldecoder = PyxlIncrementalDecoder,
        streamreader = PyxlStreamReader,
        streamwriter = utf8.streamwriter)

codecs.register(search_function)
