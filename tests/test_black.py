import os
import pytest
import tempfile

from pyxl.codec.transform import pyxl_transform_string, pyxl_invert_string

dir_path = os.path.dirname(os.path.abspath(__file__))

input_files = [
    'test_black_input.py',
]

def _black(file_name):
    import black
    path = os.path.join(dir_path, file_name)

    with open(path, "r", encoding='utf8') as f:
        contents = f.read()
    with open(path + '.exp', "r", encoding='utf8') as f:
        expected_contents = f.read()

    # Run black on the file. We manually encode and decode ourselves
    # to avoid needing to make black find the right codec.
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = os.path.join(tmp_dir, file_name)
        with open(tmp_path, "w", encoding='utf8') as f:
            f.write(pyxl_transform_string(contents, invertible=True))

        try:
            black.main([tmp_path])
        except SystemExit as e:
            pass

        with open(tmp_path, "r", encoding='utf8') as f:
            actual_contents = pyxl_invert_string(f.read())

    assert expected_contents == actual_contents, (
        "Black output did not match expected for file %s" % file_name)

# TODO: it would be better if each file was automatically a separate test case...
def test_black():
    try:
        import black
    except ImportError:
        pytest.skip()

    for file_name in input_files:
        _black(file_name)
