import glob
import os
from typing import List

import click

from launchable.test_runners import launchable
from launchable.test_runners.nunit import nunit_parse_func
from launchable.testpath import TestPath


@launchable.subset
def subset(client):
    """
    Alpha: Supports only Zero Input Subsetting
    """
    if not client.is_get_tests_from_previous_sessions:
        click.echo(
            click.style(
                "The dotnet profile only supports Zero Input Subsetting.\nMake sure to use `--get-tests-from-previous-sessions` opton",  # noqa: E501
                fg="red"),
            err=True)

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
            paths.append(path.get("name", ""))

        return prefix + ".".join(paths)

    def exclusion_output_handler(subset_tests: List[TestPath], rest_tests: List[TestPath]):
        if client.rest:
            with open(client.rest, "w+", encoding="utf-8") as fp:
                fp.write(client.separator.join(formatter(t) for t in subset_tests))

        click.echo(client.separator.join(formatter(t) for t in rest_tests))

    client.separator = separator
    client.formatter = formatter
    client.exclusion_output_handler = exclusion_output_handler
    client.run()


@launchable.split_subset
def split_subset(client):
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
            paths.append(path.get("name", ""))

        return prefix + ".".join(paths)

    def exclusion_output_handler(subset_tests: List[TestPath], rest_tests: List[TestPath]):
        if client.rest:
            with open(client.rest, "w+", encoding="utf-8") as fp:
                fp.write(client.separator.join(formatter(t) for t in subset_tests))

        click.echo(client.separator.join(formatter(t) for t in rest_tests))

    client.separator = separator
    client.formatter = formatter
    client.exclusion_output_handler = exclusion_output_handler
    client.run()


@click.argument('files', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, files):
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
            click.echo("No matches found: {}".format(file), err=True)

    # Note: we support only Nunit test report format now.
    # If we need to support another format e.g) JUnit, trc, then we'll add a option
    client.parse_func = nunit_parse_func
    client.run()
