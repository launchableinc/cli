from typing import List
from os.path import *
import click
import os
import glob
from . import launchable
from ..utils.file_name_pattern import pytest_test_pattern

# Please specify junit_family=legacy for pytest report format. if using pytest version 6 or higher.
# - pytest has changed its default test report format from xunit1 to xunit2 since version 6.
#   - https://docs.pytest.org/en/latest/deprecations.html#junit-family-default-value-change-to-xunit2
# - The xunit2 format no longer includes file names.
#   - It is possible to output in xunit1 format by specifying junit_family=legacy.
#   - The xunit1 format includes the file name.


@click.argument('source_roots', required=False, nargs=-1)
@launchable.subset
def subset(client, source_roots: List[str]):
    if not source_roots:
        # for Example
        # $ pytest --collect-only -q
        # > tests/test_mod.py::TestClass::test__can_print_aaa
        # > tests/fooo/func4_test.py::test_func6
        # >
        # > 2 tests collected in 0.02s
        #
        # result.xml(junit)
        # <testcase classname="tests.fooo.func4_test" name="test_func6" file="tests/fooo/func4_test.py" line="0" time="0.000" />
        # <testcase classname="tests.test_mod.TestClass" name="test__can_print_aaa" file="tests/test_mod.py" line="3" time="0.001" />
        for label in client.stdin():
            label = label.rstrip()
            # When an empty line comes, it's done.
            if not label:
                break
            data = label.split("::")
            test_path = [
                {"type": "file", "name": os.path.normpath(data[0])},
                {"type": "testcase", "name": data[-1]},
            ]
            # tests/fooo/func4_test.py -> tests.fooo.func4_test
            class_name = os.path.splitext(os.path.normpath(data[0]))[
                0].replace(os.sep, ".")
            if len(data) == 3:
                # tests/test_mod.py::TestClass::test__can_print_aaa -> tests.test_mod.TestClass
                class_name += "." + data[1]
            test_path.append({"type": "class", "name": class_name})
            client.test_path(test_path)
    else:
        def add(f: str):
            if pytest_test_pattern.match(basename(f)):
                client.test_path(
                    [{"type": "file", "name": os.path.normpath(f)}])
        for root in source_roots:
            for b in glob.iglob(root):
                if isdir(b):
                    for t in glob.iglob(join(b, '**/*.py'), recursive=True):
                        add(t)
                else:
                    add(b)
    client.formatter = lambda x: "{}".format(x)
    client.run()


split_subset = launchable.CommonSplitSubsetImpls(__name__).split_subset()

record_tests = launchable.CommonRecordTestImpls(__name__).report_files()
