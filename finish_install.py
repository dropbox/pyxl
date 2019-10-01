import shutil
import sys
import os.path
from distutils.sysconfig import get_python_lib

python_lib = get_python_lib()
if len(sys.argv) > 1 and sys.argv[1] == '--invertible':
    module = 'register_invertible'
else:
    module = 'register'

with open(os.path.join(python_lib, 'pyxl.pth'), 'w') as f:
    f.write('import pyxl.codec.{}\n'.format(module))
