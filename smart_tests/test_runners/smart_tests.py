import glob
import os
import sys
import types

import typer

from smart_tests.commands.record.tests import app as record_tests_cmd
from smart_tests.commands.split_subset import app as split_subset_cmd
from smart_tests.commands.subset import app as subset_cmd


def cmdname(m):
    """figure out the sub-command name from a test runner function"""

    # a.b.cde -> cde
    # xyz -> xyz
    #
    # In python module name the conventional separator is '_' but in command name,
    # it is '-', so we do replace that
    return m[m.rfind('.') + 1:].replace('_', '-')


def wrap(f, group, name=None):
    """
    Wraps a 'plugin' function into a typer command and registers it to the given group.

    a plugin function receives the scanner object in its first argument
    """
    if not name:
        name = cmdname(f.__module__)

    # All functions are now Typer functions - no more Click detection needed
    # We need to preserve the original function's signature for Typer to work properly
    import inspect
    from functools import wraps

    # Get the original function signature (excluding 'client' parameter)
    sig = inspect.signature(f)
    params = list(sig.parameters.values())[1:]  # Skip 'client' parameter

    # Create a wrapper that matches the original signature
    @wraps(f)
    def typer_wrapper(ctx: typer.Context, *args, **kwargs):
        client = ctx.obj

        # Store the test runner name in the client object for later use
        if hasattr(client, 'set_test_runner'):
            client.set_test_runner(name)

        # Call the function with client as first argument, then remaining args
        return f(client, *args, **kwargs)

    # Copy parameter annotations from original function (excluding client)
    new_params = [inspect.Parameter('ctx', inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=typer.Context)]
    new_params.extend(params)
    typer_wrapper.__signature__ = sig.replace(parameters=new_params)

    # Register the command with the Typer app
    cmd = group.command(name=name)(typer_wrapper)
    return cmd


def subset(f):
    return wrap(f, subset_cmd)


record = types.SimpleNamespace()
record.tests = lambda f: wrap(f, record_tests_cmd)


def split_subset(f):
    return wrap(f, split_subset_cmd)


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
        def subset(client, files: list[str]):
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

        def record_tests(client, source_roots: list[str]):
            CommonRecordTestImpls.load_report_files(client=client, source_roots=source_roots, file_mask=file_mask)

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
                typer.echo("No matches found: {}".format(root), err=True)
                # intentionally exiting with zero
                return

        client.run()


class CommonSplitSubsetImpls:
    def __init__(
            self,
            module_name,
            formatter=None,
            seperator=None,
            same_bin_formatter=None,
    ):
        self.cmdname = cmdname(module_name)
        self._formatter = formatter
        self._separator = seperator
        self._same_bin_formatter = same_bin_formatter

    def split_subset(self):
        def split_subset(client, files=None):
            # client type: SplitSubset in def
            # lauchable.commands.split_subset.split_subset
            if self._formatter:
                client.formatter = self._formatter

            if self._separator:
                client.separator = self._separator

            if self._same_bin_formatter:
                client.same_bin_formatter = self._same_bin_formatter

            client.run(test_runner_name=self.cmdname)

        return wrap(split_subset, split_subset_cmd, self.cmdname)
