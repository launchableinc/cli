import glob
import os
import re
from typing import Dict, List

import click
from junitparser import TestCase, TestSuite  # type: ignore

from ..testpath import TestPath
from ..utils.logger import Logger
from . import launchable


@launchable.subset
def subset(client):
    logger = Logger()

    # NOTE: This should be using package name + test function name to specify
    # which tests to run. However, the initial integration is created so that we
    # only specify the test function names. This can result in matching some
    # extra tests in multiple packages. However, in order to keep the initial
    # way of the integration, we cannot change this. Try to do the best.
    test_cases = []
    pattern = re.compile('\\s+')
    for line in client.stdin():
        if ' ' not in line:
            test_cases.append(line.strip('\n'))
        else:
            parts = pattern.split(line)
            if len(parts) >= 2:
                package = parts[1].split('/')[-1]
                for test_case in test_cases:
                    client.test_path([{'type': 'class', 'name': package}, {
                                     'type': 'testcase', 'name': test_case}])
            else:
                logger.warning("Cannot extract the package from the input. This may result in missing some tests.")
            test_cases = []
    client.formatter = lambda x: "^{}$".format(x[1]['name'])
    client.separator = '|'
    client.run()


@click.argument('source_roots', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, source_roots):
    for root in source_roots:
        match = False
        for t in glob.iglob(root, recursive=True):
            match = True
            if os.path.isdir(t):
                client.scan(t, "*.xml")
            else:
                client.report(t)

        if not match:
            click.echo("No matches found: {}".format(root), err=True)
            return

    default_path_builder = client.path_builder

    def path_builder(case: TestCase, suite: TestSuite, report_file: str) -> TestPath:
        tp = default_path_builder(case, suite, report_file)
        for tpc in tp:
            if 'type' in tpc and 'name' in tpc and tpc['type'] == 'class':
                # go-junit-report v2 reports full package name. go-junit-report
                # v1 reports only the last component of the package name. In
                # order to make this backward compatible, we align this to v1.
                tpc['name'] = tpc['name'].split('/')[-1]
        return tp

    client.path_builder = path_builder
    client.run()


def format_same_bin(s: str) -> List[Dict[str, str]]:
    t = s.split(".")
    return [{"type": "class", "name": t[0]},
            {"type": "testcase", "name": t[1]}]


split_subset = launchable.CommonSplitSubsetImpls(
    __name__,
    formatter=lambda x: "^{}$".format(x[1]['name']),
    seperator='|',
    same_bin_formatter=format_same_bin,
).split_subset()
