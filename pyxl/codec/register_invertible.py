import codecs


def search_function(encoding):
    if encoding != 'pyxl': return None

    from pyxl.codec.transform import (
        pyxl_encode, pyxl_decode, PyxlIncrementalDecoderInvertible, PyxlIncrementalEncoder,
        PyxlStreamReaderInvertible, PyxlStreamWriter,
    )

    return codecs.CodecInfo(
        name = 'pyxl',
        encode = pyxl_encode,
        decode = lambda b: pyxl_decode(b, invertible=True),
        incrementalencoder = PyxlIncrementalEncoder,
        incrementaldecoder = PyxlIncrementalDecoderInvertible,
        streamreader = PyxlStreamReaderInvertible,
        streamwriter = PyxlStreamWriter,
    )


codecs.register(search_function)
