#
# The the test runner to support playwright junit report format.
# https://playwright.dev/
#
import click
from junitparser import TestCase, TestSuite  # type: ignore

from ..testpath import TestPath
from . import launchable


@click.argument('reports', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, reports):
    def path_builder(case: TestCase, suite: TestSuite,
                     report_file: str) -> TestPath:
        """
        The playwright junit report sets a file name to the name attribute in a testsuite element and the classname attribute in a testcase element. # noqa: E501
        This playwright plugin uses a testsuite attribute value.
        e.g.)
        <testsuite name="tests/demo-todo-app.spec.ts" ...>
            <testcase name="New Todo › should allow me to add todo items" classname="tests/demo-todo-app.spec.ts"></testcase>
            <testcase name="New Todo › should clear text input field when an item is added" classname="tests/demo-todo-app.spec.ts"></testcase>
        </testsuite>
        """
        filepath = suite.name
        if not filepath:
            raise click.ClickException(
                "No file name found in %s" % report_file)

        test_path = [client.make_file_path_component(filepath)]
        if case.name:
            test_path.append({"type": "testcase", "name": case.name})
        return test_path
    client.path_builder = path_builder

    for r in reports:
        client.report(r)
    client.run()


@launchable.subset
def subset(client):
    # read lines as test file names
    for t in client.stdin():
        client.test_path(t.rstrip("\n"))

    client.run()


split_subset = launchable.CommonSplitSubsetImpls(__name__).split_subset()
