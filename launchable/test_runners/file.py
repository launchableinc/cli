#
# The most bare-bone versions of the test runner support
#
import click
from junitparser import TestCase, TestSuite # type: ignore

from . import launchable
from ..engine import Optimize
from ..testpath import TestPath


@launchable.optimize
class FileOptimize(Optimize):
    # TODO: think about a proper name
    # allow Click options
    def enumerate_tests(self):
        # read lines as test file names
        for t in self.stdin():
            self.test_path(t.rstrip("\n"))

@click.argument('reports', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, reports):
    def path_builder(case: TestCase, suite: TestSuite, report_file: str) -> TestPath:
        """path builder that puts the file name first, which is consistent with the subset command"""
        def find_filename():
            """look for what looks like file names from test reports"""
            for e in [case, suite]:
                for a in ["file","filepath"]:
                    filepath = e._elem.attrib.get(a)
                    if filepath:
                        return filepath
            return None # failing to find a test name


        filepath = find_filename()
        if not filepath:
            raise click.ClickException("No file name found in %s" % report_file)

        # default test path in `subset` expects to have this file name
        test_path = [client.make_file_path_component(filepath)]
        if suite.name:
            test_path.append({"type": "testsuite", "name": suite.name})
        if case.name:
            test_path.append({"type": "testcase", "name": case.name})
        return test_path
    client.path_builder = path_builder

    for r in reports:
        client.report(r)
    client.run()


