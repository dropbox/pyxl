import codecs, io, encodings
import sys
import traceback
from encodings import utf_8
from pyxl.codec.tokenizer import (
    pyxl_invert_tokenize, pyxl_tokenize, pyxl_untokenize,
    PyxlUnfinished,
)

def pyxl_transform(stream, invertible=False):
    try:
        output = pyxl_untokenize(pyxl_tokenize(stream.readline, invertible))
    except Exception as ex:
        print(ex)
        traceback.print_exc()
        raise

    return output


def pyxl_invert(stream):
    try:
        output = pyxl_untokenize(pyxl_invert_tokenize(stream.readline))
    except PyxlUnfinished:
        raise
    except Exception as ex:
        print(ex)
        traceback.print_exc()
        raise

    return output


def pyxl_transform_string(input, invertible=False):
    stream = io.StringIO(input)
    return pyxl_transform(stream, invertible)


def pyxl_invert_string(input):
    stream = io.StringIO(input)
    return pyxl_invert(stream)


def pyxl_encode(input, errors='strict'):
    # FIXME: maybe we should actually be able to consume partial results
    # instead of this O(n^2) retry thing?
    try:
        return pyxl_invert_string(input).encode('utf-8'), len(input)
    except PyxlUnfinished:
        return b'', 0


def pyxl_decode(input, errors='strict', invertible=False):
    return pyxl_transform_string(bytes(input).decode('utf-8'), invertible), len(input)


class PyxlIncrementalDecoder(codecs.BufferedIncrementalDecoder):
    invertible = False

    def decode(self, input, final=False):
        self.buffer += input
        if final:
            buff = self.buffer
            self.buffer = b''
            return pyxl_transform_string(buff.decode('utf-8'), self.invertible)
        else:
            return ''


class PyxlIncrementalDecoderInvertible(PyxlIncrementalDecoder):
    invertible = True


class PyxlIncrementalEncoder(codecs.BufferedIncrementalEncoder):
    def _buffer_encode(self, input, errors, final):
        return pyxl_encode(input, errors)


class PyxlStreamReader(utf_8.StreamReader):
    decode = pyxl_decode


class PyxlStreamReaderInvertible(utf_8.StreamReader):
    decode = lambda input, errors='strict': pyxl_decode(input, errors, invertible=True)


class PyxlStreamWriter(codecs.StreamWriter):
    encode = pyxl_encode
