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

class PyxlStreamReader(utf_8.StreamReader):
    def __init__(self, *args, **kwargs):
        codecs.StreamReader.__init__(self, *args, **kwargs)

        try:
            data = tokenize.untokenize(pyxl_tokenize(self.stream.readline))
        except Exception, ex:
            print ex
            raise

        self.stream = cStringIO.StringIO(data)

def search_function(encoding):
    if encoding != 'pyxl': return None
    # Assume utf8 encoding
    utf8=encodings.search_function('utf8')
    return codecs.CodecInfo(
        name = 'pyxl',
        encode = utf8.encode,
        decode = utf8.decode,
        incrementalencoder = utf8.incrementalencoder,
        incrementaldecoder = utf8.incrementaldecoder,
        streamreader = PyxlStreamReader,
        streamwriter = utf8.streamwriter)

codecs.register(search_function)
