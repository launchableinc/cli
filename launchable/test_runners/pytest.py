from typing import List
import click, glob, os

from click.termui import style
from . import launchable
from ..utils.file_name_pattern import pytest_test_pattern

@click.argument('source_roots', required=True, nargs=-1)
@launchable.subset
def subset(client, source_roots: List[str]):
    for root in source_roots:
        client.scan(root.rstrip('/'), "**/*.py", lambda f: f if pytest_test_pattern.match(f) else False)

    client.run()

@click.argument('source_roots', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, source_roots):
    # Accept both file names and GLOB patterns
    # Simple globs like '*.xml' can be dealt with by shell, but
    # not all shells consistently deal with advanced GLOBS like '**'
    # so it's worth supporting it here.
    for root in source_roots:
        match = False
        for t in glob.iglob(root, recursive=True):
            match = True
            if os.path.isdir(t):
                client.scan(t, "*.xml")
            else:
                client.report(t)

        if not match:
            # By following the shell convention, if the file doesn't exist or GLOB doesn't match anything,
            # raise it as an error. Note this can happen for reasons other than a configuration error.
            # For example, if a build catastrophically failed and no tests got run.
            click.echo("No matches found: {}".format(root), err=True)
            # intentionally exiting with zero
            return
    for case in client.parse_func(client.reports[0]):
      if not [x for x in case['testPath'] if x['type'] == 'file']:
        raise click.UsageError(
          os.linesep.join([
          click.style("The file attribute was not found in the test result report.", fg="red"),
          click.style("If you are using Pytest 6.0 or higher, please specify a junit_family other than xunit2. SEE: ", fg="red") +
          click.style("https://docs.pytest.org/en/latest/deprecations.html#junit-family-default-value-change-to-xunit2", fg="cyan", underline=True),
          click.style("For example: ", fg="red") + click.style("$ pytest -o junit_family=legacy --junit-xml=test-results/junit.xml", bg="black", fg="green")
          ])
        )

    client.run()
