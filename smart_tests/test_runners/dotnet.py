import glob
import os
from typing import Annotated, List

import typer

from smart_tests.test_runners import smart_tests
from smart_tests.test_runners.nunit import nunit_parse_func
from smart_tests.testpath import TestPath


# main subset logic
def do_subset(client, bare):
    if bare:
        separator = "\n"
        prefix = ""
    else:
        # LEGACY: we recommend the bare mode with native NUnit integration
        # ref: https://github.com/Microsoft/vstest-docs/blob/main/docs/filter.md
        separator = "|"
        prefix = "FullyQualifiedName="

        if client.is_output_exclusion_rules:
            separator = "&"
            prefix = "FullyQualifiedName!="

    def formatter(test_path: TestPath):
        paths = []

        for path in test_path:
            t = path.get("type", "")
            if t == 'Assembly':
                continue
            if t == 'ParameterizedMethod':
                # For parameterized test, we get something like
                # Assembly=calc.dll#TestSuite=SomeNamespace#TestSuite=TestClassName#ParameterizedMethod=DivideTest#TestCase=DivideTest(1,3)
                # see record_test_result.json as an example.
                continue
            paths.append(path.get("name", ""))

        return prefix + ".".join(paths)

    def exclusion_output_handler(subset_tests: List[TestPath], rest_tests: List[TestPath]):
        if client.rest:
            with open(client.rest, "w+", encoding="utf-8") as fp:
                fp.write(client.separator.join(formatter(t) for t in subset_tests))

        typer.echo(client.separator.join(formatter(t) for t in rest_tests))

    client.separator = separator
    client.formatter = formatter
    client.exclusion_output_handler = exclusion_output_handler
    client.run()


@smart_tests.subset
def subset(
    client,
    bare: Annotated[bool, typer.Option(
        "--bare",
        help="outputs class names alone"
    )] = False,
):
    """
    Alpha: Supports only Zero Input Subsetting
    """
    if not client.is_get_tests_from_previous_sessions:
        typer.secho(
            "The dotnet profile only supports Zero Input Subsetting.\nMake sure to use "
            "`--get-tests-from-previous-sessions` option",
            fg=typer.colors.RED,
            err=True)
        raise typer.Exit(1)

    do_subset(client, bare)


@smart_tests.record.tests
def record_tests(
    client,
    files: Annotated[List[str], typer.Argument(
        help="Test report files to process"
    )],
):
    """
    Alpha: Supports only NUnit report formats.
    """
    for file in files:
        match = False
        for t in glob.iglob(file, recursive=True):
            match = True
            if os.path.isdir(t):
                client.scan(t, "*.xml")
            else:
                client.report(t)
        if not match:
            typer.echo(f"No matches found: {file}", err=True)

    # Note: we support only Nunit test report format now.
    # If we need to support another format e.g) JUnit, trc, then we'll add a option
    client.parse_func = nunit_parse_func
    client.run()
