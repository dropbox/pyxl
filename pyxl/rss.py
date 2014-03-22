import datetime

from pyxl.utils import escape
from pyxl.base import x_base

class x_rss_element(x_base):
    def _to_list(self, l):
        l.extend((u'<', self.__tag__))
        for name, value in self.__attributes__.iteritems():
            name, value = self._handle_attribute(name, value)
            l.extend((u' ', name, u'="', escape(value), u'"'))
        l.append(u'>')

        for child in self.__children__:
            x_base._render_child_to_list(child, l)

        l.extend((u'</', self.__tag__, u'>'))

    def _handle_attribute(self, name, value):
        return (name, value)

class x_rss_decl_standalone(x_base):
    def _to_list(self, l):
        l.append('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>')

class x_rss(x_rss_element):
    __attrs__ = {
        'version':unicode
    }

class x_channel(x_rss_element):
    pass

class x_title(x_rss_element):
    pass

class x_link(x_rss_element):
    pass

class x_description(x_rss_element):
    pass

class x_language(x_rss_element):
    pass

class x_rss_date_element(x_base):
    __attrs__ = {
            'date':datetime.datetime
        }

    def _to_list(self, l):
        l.extend((u'<', self.__tag__, '>'))
        l.append(unicode(self.date.strftime('%a, %d %b %Y %H:%M:%S GMT')))
        l.extend((u'</', self.__tag__, u'>'))

class x_lastBuildDate(x_rss_date_element):
    pass

class x_pubDate(x_rss_date_element):
    pass

class x_ttl(x_rss_element):
    pass

class x_item(x_rss_element):
    pass

class x_guid(x_rss_element):
    __attrs__ = {
        'is-perma-link':bool
    }

    def _handle_attribute(self, name, value):
        # This is needed because pyxl doesn't support mixed case attribute names.
        if name == 'is-perma-link':
            return ('isPermaLink', 'true' if value else 'false')
        else:
            return (name, value)
