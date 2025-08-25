import glob
import os
import sys
import types
from typing import Annotated

import typer

from smart_tests.commands.record.tests import app as record_tests_cmd
from smart_tests.commands.subset import app as subset_cmd
from smart_tests.utils.test_runner_registry import cmdname, create_test_runner_wrapper, get_registry


# Legacy wrap function for CommonImpls classes
def wrap(f, group, name=None):
    """Legacy wrapper function for CommonImpls classes."""
    if not name:
        name = cmdname(f.__module__)
    wrapper = create_test_runner_wrapper(f, name)
    cmd = group.command(name=name)(wrapper)
    return cmd


# NestedCommand-only decorators (no backward compatibility)
def subset(f):
    """
    Register a subset function with the test runner registry.

    This stores the function for later dynamic command generation in NestedCommand.
    """
    test_runner_name = cmdname(f.__module__)
    registry = get_registry()
    registry.register_subset(test_runner_name, f)
    return f


record = types.SimpleNamespace()


def _record_tests_decorator(f):
    """Register a record tests function with the test runner registry."""
    test_runner_name = cmdname(f.__module__)
    registry = get_registry()
    registry.register_record_tests(test_runner_name, f)
    return f


record.tests = _record_tests_decorator


class CommonSubsetImpls:
    """
    Typical 'subset' implementations that are reusable.
    """

    def __init__(self, module_name):
        self.cmdname = cmdname(module_name)

    def scan_files(self, pattern):
        """
        Suitable for test runners that use files as unit of tests where file names follow a naming pattern.

        :param pattern: file masks that identify test files, such as '*_spec.rb'
        """
        def subset(
            client,
            files: Annotated[list[str], typer.Argument(
                help="Test files or directories to include in the subset"
            )]
        ):
            # client type: Optimize in def lauchable.commands.subset.subset
            def parse(fname: str):
                if os.path.isdir(fname):
                    client.scan(fname, '**/' + pattern)
                elif fname == '@-':
                    # read stdin
                    for line in sys.stdin:
                        parse(line.rstrip())
                elif fname.startswith('@'):
                    # read response file
                    with open(fname[1:]) as f:
                        for line in f:
                            parse(line.rstrip())
                else:
                    # assume it's a file
                    client.test_path(fname)

            for f in files:
                parse(f)

            client.run()

        # Register with new registry system for NestedCommand
        registry = get_registry()
        registry.register_subset(self.cmdname, subset)

        return wrap(subset, subset_cmd, self.cmdname)


class CommonRecordTestImpls:
    """
    Typical 'record tests' implementations that are reusable.
    """

    def __init__(self, module_name):
        self.cmdname = cmdname(module_name)

    def report_files(self, file_mask="*.xml"):
        """
        Suitable for test runners that create a directory full of JUnit report files.

        'record tests' expect JUnit report/XML file names.
        """

        def record_tests(
            client,
            source_roots: Annotated[list[str], typer.Argument(
                help="Source directories containing test report files"
            )]
        ):
            CommonRecordTestImpls.load_report_files(client=client, source_roots=source_roots, file_mask=file_mask)

        # Register with new registry system for NestedCommand
        registry = get_registry()
        registry.register_record_tests(self.cmdname, record_tests)

        return wrap(record_tests, record_tests_cmd, self.cmdname)

    @classmethod
    def load_report_files(cls, client, source_roots, file_mask="*.xml"):
        # client type: RecordTests in def launchable.commands.record.tests.tests
        # Accept both file names and GLOB patterns
        # Simple globs like '*.xml' can be dealt with by shell, but
        # not all shells consistently deal with advanced GLOBS like '**'
        # so it's worth supporting it here.
        for root in source_roots:
            match = False
            for t in glob.iglob(root, recursive=True):
                match = True
                if os.path.isdir(t):
                    client.scan(t, file_mask)
                else:
                    client.report(t)

            if not match:
                # By following the shell convention, if the file doesn't exist or GLOB doesn't match anything,
                # raise it as an error. Note this can happen for reasons other than a configuration error.
                # For example, if a build catastrophically failed and no
                # tests got run.
                typer.echo(f"No matches found: {root}", err=True)
                # intentionally exiting with zero
                return

        client.run()
