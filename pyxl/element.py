#!/usr/bin/env python

from pyxl.base import x_base

class x_element(x_base):

    _element = None  # render() output cached by _rendered_element()

    def _get_base_element(self):
        # Adding classes costs ~10%
        out = self._rendered_element()
        # Note: get_class() may return multiple space-separated classes.
        cls = self.get_class()
        classes = set(cls.split(' ')) if cls else set()

        while isinstance(out, x_element):
            new_out = out._rendered_element()
            cls = out.get_class()
            if cls:
                classes.update(cls.split(' '))
            out = new_out

        if classes and isinstance(out, x_base):
            classes.update(out.get_class().split(' '))
            out.set_attr('class', ' '.join(filter(None, classes)))

        return out

    def _to_list(self, l):
        self._render_child_to_list(self._get_base_element(), l)

    def _rendered_element(self):
        if self._element is None:
            self._element = self.render()
        return self._element

    def render(self):
        raise NotImplementedError()
