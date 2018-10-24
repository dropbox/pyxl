import codecs

def search_function(encoding):
    if encoding != 'pyxl':
        return None
    import pyxl.codec.register
    return pyxl.codec.register.search_function(encoding)

codecs.register(search_function)
