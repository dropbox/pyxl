#!/usr/bin/env python

import sys

from pyxl.utils import escape

# We need a way to ensure that on a given page, no two pyxl elements are given the
# same 'pyxl<num>' id. Using a random number generator works reasonably well, but
# introduces extra complexity and overhead that is unnecessary. A global variable
# counter works just as well and is much faster. Since we only care about collisions
# in a single page, we don't have to worry about two different instances having the
# same counters.
pyxl_id_counter = 0

class PyxlException(Exception):
    pass

class x_base_metaclass(type):
    def __init__(self, name, parents, attrs):
        super(x_base_metaclass, self).__init__(name, parents, attrs)
        x_base_parents = [parent for parent in parents if hasattr(parent, '__attrs__')]
        parent_attrs = x_base_parents[0].__attrs__ if len(x_base_parents) else {}
        self_attrs = self.__dict__.get('__attrs__', {})

        # Dont allow '_' in attr names
        for attr_name in self_attrs:
            assert '_' not in attr_name, (
                "%s: '_' not allowed in attr names, use '-' instead" % attr_name)

        combined_attrs = dict(parent_attrs)
        combined_attrs.update(self_attrs)
        setattr(self, '__attrs__', combined_attrs)
        setattr(self, '__tag__', name[2:])

class x_base(object):

    __metaclass__ = x_base_metaclass
    __attrs__ = {
        # HTML attributes
        'accesskey': unicode,
        'class': unicode,
        'dir': unicode,
        'id': unicode,
        'lang': unicode,
        'maxlength': unicode,
        'role': unicode,
        'style': unicode,
        'tabindex': int,
        'title': unicode,
        'xml:lang': unicode,

        # JS attributes
        'onabort': unicode,
        'onblur': unicode,
        'onchange': unicode,
        'onclick': unicode,
        'ondblclick': unicode,
        'onerror': unicode,
        'onfocus': unicode,
        'onkeydown': unicode,
        'onkeypress': unicode,
        'onkeyup': unicode,
        'onload': unicode,
        'onmousedown': unicode,
        'onmouseenter': unicode,
        'onmouseleave': unicode,
        'onmousemove': unicode,
        'onmouseout': unicode,
        'onmouseover': unicode,
        'onmouseup': unicode,
        'onreset': unicode,
        'onresize': unicode,
        'onselect': unicode,
        'onsubmit': unicode,
        'onunload': unicode,
        }

    def __init__(self, **kwargs):
        self.__attributes__ = {}
        self.__children__ = []

        for name, value in kwargs.iteritems():
            self.set_attr(x_base._fix_attribute_name(name), value)

    def __call__(self, *children):
        self.append_children(children)
        return self

    def get_id(self):
        eid = self.attr('id')
        if not eid:
            # See comment at definition of pyxl_id_counter for more details.
            global pyxl_id_counter
            eid = 'pyxl%d' % pyxl_id_counter
            pyxl_id_counter = (pyxl_id_counter + 1) % sys.maxint
            self.set_attr('id', eid)
        return eid

    def children(self, selector=None, exclude=False):
        if not selector:
            return self.__children__

        # filter by class
        if selector[0] == '.':
            select = lambda x: selector[1:] in x.get_class() 

        # filter by id
        elif selector[0] == '#':
            select = lambda x: selector[1:] == x.get_id()

        # filter by tag name
        else:
            select = lambda x: x.__class__.__name__ == ('x_%s' % selector)

        if exclude:
            func = lambda x: not select(x)
        else:
            func = select

        return filter(func, self.__children__)

    def append(self, child):
        if type(child) in (list, tuple) or hasattr(child, '__iter__'):
            self.__children__.extend(c for c in child if c is not None and c is not False)
        elif child is not None and child is not False:
            self.__children__.append(child)

    def prepend(self, child):
        if child is not None and child is not False:
            self.__children__.insert(0, child)

    def __getattr__(self, name):
        return self.attr(name.replace('_', '-'))

    def attr(self, name, default=None):
        # this check is fairly expensive (~8% of cost)
        if not self.allows_attribute(name):
            raise PyxlException('<%s> has no attr named "%s"' % (self.__tag__, name))

        value = self.__attributes__.get(name)

        if value is not None:
            return value

        attr_type = self.__attrs__.get(name, unicode)
        if type(attr_type) == list:
            if not attr_type:
                raise PyxlException('Invalid attribute definition')

            if None in attr_type[1:]:
                raise PyxlException('None must be the first, default value')

            return attr_type[0]

        return default

    def transfer_attributes(self, element):
        for name, value in self.__attributes__.iteritems():
            if element.allows_attribute(name) and element.attr(name) is None:
                element.set_attr(name, value)

    def set_attr(self, name, value):
        # this check is fairly expensive (~8% of cost)
        if not self.allows_attribute(name):
            raise PyxlException('<%s> has no attr named "%s"' % (self.__tag__, name))

        if value is not None:
            attr_type = self.__attrs__.get(name, unicode)

            if type(attr_type) == list:
                # support for enum values in pyxl attributes
                values_enum = attr_type
                assert values_enum, 'Invalid attribute definition'

                if value not in values_enum:
                    msg = '%s: %s: incorrect value "%s" for "%s". Expecting enum value %s' % (
                        self.__tag__, self.__class__.__name__, value, name, values_enum)
                    raise PyxlException(msg)

            else:
                try:
                    # Validate type of attr and cast to correct type if possible
                    value = value if isinstance(value, attr_type) else attr_type(value)
                except Exception:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    msg = '%s: %s: incorrect type for "%s". expected %s, got %s' % (
                        self.__tag__, self.__class__.__name__, name, attr_type, type(value))
                    exception = PyxlException(msg)
                    raise exception, None, exc_tb

            self.__attributes__[name] = value

        elif name in self.__attributes__:
            del self.__attributes__[name]

    def get_class(self):
        return self.attr('class', '')

    def add_class(self, xclass):
        if not xclass: return
        current_class = self.attr('class')
        if current_class: current_class += ' ' + xclass
        else: current_class = xclass
        self.set_attr('class', current_class)

    def append_children(self, children):
        for child in children:
            self.append(child)

    def attributes(self):
        return self.__attributes__

    def set_attributes(self, attrs_dict):
        for name, value in attrs_dict.iteritems():
            self.set_attr(name, value)

    def allows_attribute(self, name):
        return (name in self.__attrs__ or name.startswith('data-') or name.startswith('aria-'))

    def to_string(self):
        l = []
        self._to_list(l)
        return u''.join(l)

    def _to_list(self, l):
        raise NotImplementedError()

    def __str__(self):
        return self.to_string()

    def __unicode__(self):
        return self.to_string()

    @staticmethod
    def _render_child_to_list(child, l):
        if isinstance(child, x_base): child._to_list(l)
        elif child is not None: l.append(escape(child))

    @staticmethod
    def _fix_attribute_name(name):
        if name == 'xclass': return 'class'
        if name == 'xfor': return 'for'
        return name.replace('_', '-').replace('COLON', ':')
