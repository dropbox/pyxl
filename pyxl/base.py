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

import sys
import random
from pyxl.utils import escape

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

        self_attrs.update(parent_attrs)
        setattr(self, '__attrs__', self_attrs)
        setattr(self, '__tag__', name[2:])

class x_base(object):

    __metaclass__ = x_base_metaclass
    __attrs__ = {
        'id': unicode,
        'class': unicode,
        'style': unicode,
        'onclick': unicode,
        'ondblclick': unicode,
        'onmouseup': unicode,
        'onmousedown': unicode,
        'onmouseover': unicode,
        'onmouseout': unicode,
        'title': unicode,
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
            eid = 'pyxl%d' % random.randint(0, sys.maxint)
            self.set_attr('id', eid)
        return eid

    def children(self, selector=None):
        if not selector:
            return self.__children__

        # filter by class
        if selector[0] == '.':
            class_name = selector[1:]
            return [c for c in self.__children__
                    if class_name in c.get_class()]

        # filter by id
        if selector[0] == '#':
            id_name = selector[1:]
            return [c for c in self.__children__
                    if c.get_id() == id_name]

        # filter by tag name
        tag_name = 'x_%s' % selector
        return [c for c in self.__children__
                if c.__class__.__name__ == tag_name]

    def append(self, child):
        if type(child) in (list, tuple):
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
            raise Exception('<%s> has no attr named "%s"' % (self.__tag__, name))
        return self.__attributes__.get(name, default)

    def set_attr(self, name, value):
        # this check is fairly expensive (~8% of cost)
        if not self.allows_attribute(name):
            raise Exception('<%s> has no attr named "%s"' % (self.__tag__, name))
        if value is not None:
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

    def set_attributes(self, **kwargs):
        for name, value in kwargs.iteritems():
            self.set_attr(name, value)

    def allows_attribute(self, name):
        return (name in self.__attrs__ or name.startswith('data-') or name.startswith('aria-'))

    def to_string(self):
        raise NotImplementedError()

    def __str__(self):
        return self.to_string().encode('utf8')

    def __unicode__(self):
        return self.to_string()

    @staticmethod
    def render_child(child):
        if isinstance(child, x_base): return child.to_string()
        if child is None: return u''
        return escape(child)

    @staticmethod
    def _fix_attribute_name(name):
        if name == 'xclass': return 'class'
        if name == 'xfor': return 'for'
        return name.replace('_', '-').replace('COLON', ':')
