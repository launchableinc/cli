import glob
import json
import pathlib
from platform import node
from typing import Generator, List
from os.path import *
import subprocess
import click
import os

from launchable.commands.record.case_event import CaseEvent, CaseEventType
from launchable.testpath import TestPath
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

            test_path = _parse_pytest_nodeid(line)
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


def _parse_pytest_nodeid(nodeid: str) -> TestPath:
    data = nodeid.split("::")
    file = data[0]
    class_name = _path_to_class_name(file)
    normalized_file = os.path.normpath(file)

    # file name only
    if len(data) == 1:
        return [
            {"type": "file", "name": normalized_file},
            {"type": "class", "name": class_name},
        ]
    # file + testcase, or file + class + testcase
    else:
        testcase = data[-1]
        if len(data) == 3:
            class_name += "." + data[1]

        return [
            {"type": "file", "name": normalized_file},
            {"type": "class", "name": class_name},
            {"type": "testcase", "name": testcase},
        ]


def _path_to_class_name(path):
    '''
    tests/fooo/func4_test.py -> tests.fooo.func4_test
    '''
    return os.path.splitext(os.path.normpath(path))[0].replace(os.sep, ".")


def _pytest_formatter(test_path):
    for path in test_path:
        t = path.get('type', '')
        n = path.get('name', '')
        if t == 'class':
            cls_name = n
        elif t == 'testcase':
            case = n
        elif t == 'file':
            file = n
    # If there is no class, junitformat use package name, but pytest will be omitted
    # pytest -> tests/fooo/func4_test.py::test_func6
    # junitformat -> <testcase classname="tests.fooo.func4_test" name="test_func6" file="tests/fooo/func4_test.py" line="0" time="0.000" />
    if cls_name == _path_to_class_name(file):
        return "{}::{}".format(file, case)

    else:
        # junitformat's class name includes package, but pytest does not
        # pytest -> tests/test_mod.py::TestClass::test__can_print_aaa
        # junitformat -> <testcase classname="tests.test_mod.TestClass" name="test__can_print_aaa" file="tests/test_mod.py" line="3" time="0.001" />
        return "{}::{}::{}".format(file, cls_name.split(".")[-1], case)


split_subset = launchable.CommonSplitSubsetImpls(
    __name__, formatter=_pytest_formatter).split_subset()


@click.option('--json', 'json_report', help="use JSON report files produced by pytest-dev/pytest-reportlog", is_flag=True)
@click.argument('source_roots', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, json_report, source_roots):

    ext = "json" if json_report else "xml"
    for root in source_roots:
        match = False
        for t in glob.iglob(root, recursive=True):
            match = True
            if os.path.isdir(t):
                client.scan(t, "*.{}".format(ext))
            else:
                client.report(t)

        if not match:
            click.echo("No matches found: {}".format(root), err=True)
            return

    if json_report:
        client.parse_func = PytestJSONReportParser(client).parse_func

    client.run()


"""
If you want to use --json option, please install pytest-dev/pytest-reportlog. (https://github.com/pytest-dev/pytest-reportlog)

Usage

```
$ pip install -U pytest-reportlog
$ pytest --report-log report.json
$ launchable record tests --json report.json
```
"""


class PytestJSONReportParser:
    def __init__(self, client):
        self.client = client

    def parse_func(self, report_file: str) -> Generator[CaseEventType, None, None]:
        with open(report_file, 'r') as json_file:
            for line in json_file:
                try:
                    data = json.loads(line)
                except Exception as e:
                    raise Exception("Can't read JSON format report file {}. Make sure to confirm report file.".format(
                        report_file)) from e

                nodeid = data.get("nodeid", "")
                if nodeid == "":
                    continue

                when = data.get("when", "")
                outcome = data.get("outcome", "")

                if not (when == "call" or (when == "setup" and outcome == "skipped")):
                    continue

                status = CaseEvent.TEST_FAILED
                if outcome == "passed":
                    status = CaseEvent.TEST_PASSED
                elif outcome == "skipped":
                    status = CaseEvent.TEST_SKIPPED

                test_path = _parse_pytest_nodeid(nodeid)
                for path in test_path:
                    if path.get("type") == "file":
                        path["name"] = pathlib.Path(path["name"]).as_posix()

                yield CaseEvent.create(test_path, data.get("duration", 0), status, None, None, None, None)
