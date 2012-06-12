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

import xml.sax.saxutils
from metaserver.common import exclog2_util

xml_escape = xml.sax.saxutils.escape
xml_unescape = xml.sax.saxutils.unescape
escape_other = {
    '"': '&quot;',
    }
unescape_other = {
    '&quot;': '"',
    }

def escape(obj):
    try:
        obj = unicode(obj)
    except UnicodeDecodeError:
        exclog2_util.report_exception(severity=exclog2_util.SeverityType.CRITICAL)
        obj = unicode(obj, 'utf8')

    return xml_escape(obj, escape_other)

def unescape(obj):
    return xml_unescape(unicode(obj), unescape_other)
