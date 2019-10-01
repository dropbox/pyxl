import codecs


def search_function(encoding):
    if encoding != 'pyxl': return None

    import encodings
    from pyxl.codec.transform import pyxl_decode, PyxlIncrementalDecoder, PyxlStreamReader

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
