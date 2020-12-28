import os
import sys
from os.path import join

import click
from junitparser import TestCase, TestSuite

from . import launchable
from ..testpath import TestPath


def make_test_path(pkg, target) -> TestPath:
    return [{'type': 'package', 'name': pkg}, {'type': 'target', 'name': target}]


@launchable.subset
def subset(client):
    # Read targets from stdin, which generally looks like //foo/bar:zot
    for label in sys.stdin:
        # //foo/bar:zot -> //foo/bar & zot
        if label.startswith('//'):
            pkg, target = label.rstrip('\n').split(':')
            # TODO: error checks and more robustness
            client.test_path(make_test_path(pkg, target))

    client.formatter = lambda x: x[0]['name'] + ":" + x[1]['name']
    client.run()


@click.argument('workspace', required=True)
@launchable.record.tests
def record_tests(client, workspace):
    """
    Takes Bazel workspace, then report all its test results
    """
    base = join(workspace, 'bazel-testlogs')
    if not os.path.exists(base):
        exit("No such directory: %s" % base)

    default_path_builder = client.path_builder

    def f(case: TestCase, suite: TestSuite, report_file: str) -> TestPath:
        # In Bazel, report path name contains package & target.
        # for example, for //foo/bar:zot, the report file is at bazel-testlogs/foo/bar/zot/test.xml
        # TODO: robustness
        pkgNtarget = report_file[len(base)+1:-len("/test.xml")]

        # last path component is the target, the rest is package
        # TODO: does this work correctly when on Windows?
        path = make_test_path(os.path.dirname(pkgNtarget),
                              os.path.basename(pkgNtarget))

        # let the normal path building kicks in
        path.extend(default_path_builder(case, suite, report_file))
        return path

    client.path_builder = f

    client.scan(base, '**/test.xml')

    client.run()
