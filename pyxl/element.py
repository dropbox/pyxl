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

from pyxl.base import x_base

class x_element(x_base):
    def get_base_element(self):
        # Adding classes costs ~10%
        out = self.rendered_element()
        classes = [self.get_class()]

        while isinstance(out, x_element):
            new_out = out.rendered_element()
            classes.append(out.get_class())
            out = new_out

        if isinstance(out, x_base):
            out.add_class(' '.join(classes))

        return out

    def _to_list(self, l):
        self._render_child_to_list(self.get_base_element(), l)

    def rendered_element(self):
        if not hasattr(self, 'element'):
            self.element = self.render()
        return self.element

    def render(self):
        raise NotImplementedError()
