from typing import List
from os.path import *
import subprocess
import click
import os
from . import launchable


# Please specify junit_family=legacy for pytest report format. if using pytest version 6 or higher.
# - pytest has changed its default test report format from xunit1 to xunit2 since version 6.
#     - https://docs.pytest.org/en/latest/deprecations.html#junit-family-default-value-change-to-xunit2
# - The xunit2 format no longer includes file names.
#     - It is possible to output in xunit1 format by specifying junit_family=legacy.
#     - The xunit1 format includes the file name.
# The format of pytest changes depending on the existence of the class. They are also incompatible with the junit format.
# Therefore, it converts to junit format at the timing of sending the subset, and converts the returned value to pytest format.
# for Example
# $ pytest --collect-only -q
# > tests/test_mod.py::TestClass::test__can_print_aaa
# > tests/fooo/func4_test.py::test_func6
# >
# > 2 tests collected in 0.02s
# result.xml(junit)
# <testcase classname="tests.fooo.func4_test" name="test_func6" file="tests/fooo/func4_test.py" line="0" time="0.000" />
# <testcase classname="tests.test_mod.TestClass" name="test__can_print_aaa" file="tests/test_mod.py" line="3" time="0.001" />
#
@click.argument('source_roots', required=False, nargs=-1)
@launchable.subset
def subset(client, source_roots: List[str]):
    def _add_testpaths(lines: List[str]):
        for line in lines:
            line = line.rstrip()
            # When an empty line comes, it's done.
            if not line:
                break
            data = line.split("::")
            class_name = _path_to_class_name(data[0])
            if len(data) == 3:
                # tests/test_mod.py::TestClass::test__can_print_aaa -> tests.test_mod.TestClass
                class_name += "." + data[1]
            test_path = [
                {"type": "file", "name": os.path.normpath(data[0])},
                {"type": "class", "name": class_name},
                {"type": "testcase", "name": data[-1]},
            ]
            client.test_path(test_path)
    if not source_roots:
        _add_testpaths(client.stdin())
    else:
        command = ["pytest", "--collect-only", "-q"]
        command.extend(source_roots)
        try:
            result = subprocess.run(
                command, stdout=subprocess.PIPE, universal_newlines=True)
            _add_testpaths(result.stdout.split(os.linesep))
        except FileNotFoundError:
            raise click.ClickException(
                "pytest command not found. Please check the path.")

    client.formatter = _pytest_formatter
    client.run()


def _path_to_class_name(path):
    '''
    tests/fooo/func4_test.py -> tests.fooo.func4_test
    '''
    return os.path.splitext(os.path.normpath(path))[0].replace(os.sep, ".")


def _pytest_formatter(test_path):
    for path in test_path:
        t = path['type']
        if t == 'class':
            cls_name = path['name']
        if t == 'testcase':
            case = path['name']
        if t == 'file':
            file = path['name']
    # If there is no class, junitformat use package name, but pytest will be omitted
    # pytest -> tests/fooo/func4_test.py::test_func6
    # junitformat -> <testcase classname="tests.fooo.func4_test" name="test_func6" file="tests/fooo/func4_test.py" line="0" time="0.000" />
    if cls_name == _path_to_class_name(file):
        return "{}::{}".format(file, case)

    # junitformat's class name includes package, but pytest does not
    # pytest -> tests/test_mod.py::TestClass::test__can_print_aaa
    # junitformat -> <testcase classname="tests.test_mod.TestClass" name="test__can_print_aaa" file="tests/test_mod.py" line="3" time="0.001" />
    return "{}::{}::{}".format(file, cls_name.split(".")[-1], case)


split_subset = launchable.CommonSplitSubsetImpls(
    __name__, formatter=_pytest_formatter).split_subset()

record_tests = launchable.CommonRecordTestImpls(__name__).report_files()
