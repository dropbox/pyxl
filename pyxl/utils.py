#!/usr/bin/env python

import xml.sax.saxutils

xml_escape = xml.sax.saxutils.escape
xml_unescape = xml.sax.saxutils.unescape
escape_other = {
    '"': '&quot;',
    }
unescape_other = {
    '&quot;': '"',
    }

def escape(obj):
    return xml_escape(unicode(obj), escape_other)

def unescape(obj):
    return xml_unescape(unicode(obj), unescape_other)
