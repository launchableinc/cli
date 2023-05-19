import glob
import os
import pathlib
import sys
from os.path import join
from typing import Callable, List, Optional, TextIO, Union

import click
from tabulate import tabulate

from launchable.utils.authentication import get_org_workspace
from launchable.utils.session import parse_session

from ..testpath import FilePathNormalizer, TestPath
from ..utils.click import DURATION, PERCENTAGE, DurationType, KeyValueType, PercentageType
from ..utils.env_keys import REPORT_ERROR_KEY
from ..utils.http_client import LaunchableClient
from .helper import find_or_create_session
from .test_path_writer import TestPathWriter

# TODO: rename files and function accordingly once the PR landscape


@click.group(help="Subsetting tests")
@click.option(
    '--target',
    'target',
    help='subsetting target from 0% to 100%',
    type=PERCENTAGE,
)
@click.option(
    '--time',
    'duration',
    help='subsetting by absolute time, in seconds e.g) 300, 5m',
    type=DURATION,
)
@click.option(
    '--confidence',
    'confidence',
    help='subsetting by confidence from 0% to 100%',
    type=PERCENTAGE,
)
@click.option(
    '--session',
    'session',
    help='Test session ID',
    type=str,
)
@click.option(
    '--base',
    'base_path',
    help='(Advanced) base directory to make test names portable',
    type=click.Path(exists=True, file_okay=False),
    metavar="DIR",
)
@click.option(
    '--build',
    'build_name',
    help='build name',
    type=str,
    metavar='BUILD_NAME',
    hidden=True,
)
@click.option(
    '--rest',
    'rest',
    help='Output the subset remainder to a file, e.g. `--rest=remainder.txt`',
    type=str,
)
@click.option(
    "--flavor",
    "flavor",
    help='flavors',
    metavar='KEY=VALUE',
    cls=KeyValueType,
    multiple=True,
)
@click.option(
    "--split",
    "split",
    help='split',
    is_flag=True
)
@click.option(
    "--no-base-path-inference",
    "--no_base_path_inference",  # historical, inconsistently named
    "no_base_path_inference",
    help="""Do not guess the base path to relativize the test file paths.

    By default, if the test file paths are absolute file paths, it automatically
    guesses the repository root directory and relativize the paths. With this
    option, the command doesn't do this guess work.

    If --base_path is specified, the absolute file paths are relativized to the
    specified path irrelevant to this option. Use it if the guessed base path is
    incorrect.
    """,
    is_flag=True
)
@click.option(
    "--ignore-new-tests",
    "ignore_new_tests",
    help='Ignore tests that were added recently.\n\nNOTICE: this option will ignore tests that you added just now as well',
    is_flag=True
)
@click.option(
    "--observation",
    "is_observation",
    help="enable observation mode",
    is_flag=True,
)
@click.option(
    "--get-tests-from-previous-sessions",
    "is_get_tests_from_previous_sessions",
    help="get subset list from previous full tests",
    is_flag=True,
)
@click.option(
    "--output-exclusion-rules",
    "is_output_exclusion_rules",
    help="outputs the exclude test list. Switch the subset and rest.",
    is_flag=True,
)
@click.option(
    "--ignore-flaky-tests-above",
    "ignore_flaky_tests_above",
    help='Ignore flaky tests above the value set by this option.You can confirm flaky scores in WebApp',
    type=click.FloatRange(min=0, max=1.0),
)
@click.option(
    '--link',
    'links',
    help="Set external link of title and url",
    multiple=True,
    default=[],
    cls=KeyValueType,
)
@click.option(
    "--no-build",
    "is_no_build",
    help="If you want to only send test reports, please use this option",
    is_flag=True,
)
@click.pass_context
def subset(
    context: click.core.Context,
    target: Optional[PercentageType],
    session: Optional[str],
    base_path: Optional[str],
    build_name: Optional[str],
    rest: str,
    duration: Optional[DurationType],
    flavor: KeyValueType,
    confidence: Optional[PercentageType],
    split: bool,
    no_base_path_inference: bool,
    ignore_new_tests: bool,
    is_observation: bool,
    is_get_tests_from_previous_sessions: bool,
    is_output_exclusion_rules: bool,
    ignore_flaky_tests_above: Optional[float],
    links: List[str] = [],
    is_no_build: bool = False,
):

    if is_observation and is_get_tests_from_previous_sessions:
        click.echo(
            click.style(
                "Cannot use --observation and --get-tests-from-previous-sessions options at the same time",
                fg="red"),
            err=True,
        )
        sys.exit(1)

    session_id = find_or_create_session(
        context=context,
        session=session,
        build_name=build_name,
        flavor=flavor,
        is_observation=is_observation,
        links=links,
        is_no_build=is_no_build,
    )
    file_path_normalizer = FilePathNormalizer(base_path, no_base_path_inference=no_base_path_inference)

    # TODO: placed here to minimize invasion in this PR to reduce the likelihood of
    # PR merge hell. This should be moved to a top-level class

    TestPathWriter.base_path = base_path

    class Optimize(TestPathWriter):
        # test_paths: List[TestPath]  # doesn't work with Python 3.5
        # is_get_tests_from_previous_sessions: bool

        # Where we take TestPath, we also accept a path name as a string.
        TestPathLike = Union[str, TestPath]

        # output_handler: Callable[[
        #   List[TestPathLike], List[TestPathLike]], None]
        # exclusion_output_handler: Callable[[List[TestPathLike],
        # List[TestPathLike], bool], None]]

        def __init__(self, dry_run: bool = False):
            self.rest = rest
            self.test_paths = []  # type: List
            self.output_handler = self._default_output_handler
            self.exclusion_output_handler = self._default_exclusion_output_handler
            self.is_get_tests_from_previous_sessions = is_get_tests_from_previous_sessions
            self.is_output_exclusion_rules = is_output_exclusion_rules
            super(Optimize, self).__init__(dry_run=dry_run)

        def _default_output_handler(self, output: List[TestPath], rests: List[TestPath]):
            if rest:
                self.write_file(rest, rests)

            if output:
                self.print(output)

        def _default_exclusion_output_handler(self, subset: List[TestPath], rest: List[TestPath]):
            self.output_handler(rest, subset)

        def test_path(self, path: TestPathLike):
            def rel_base_path(path):
                if isinstance(path, str):
                    return pathlib.Path(file_path_normalizer.relativize(path)).as_posix()
                else:
                    return path

            if isinstance(path, str) and any(s in path for s in ('*', "?")):
                for i in glob.iglob(path, recursive=True):
                    if os.path.isfile(i):
                        self.test_paths.append(self.to_test_path(rel_base_path(i)))
                return

            """register one test"""
            self.test_paths.append(self.to_test_path(rel_base_path(path)))

        def stdin(self) -> Union[TextIO, List]:
            # To avoid the cli continue to wait from stdin
            if is_get_tests_from_previous_sessions:
                return []

            """
            Returns sys.stdin, but after ensuring that it's connected to something reasonable.

            This prevents a typical problem where users think CLI is hanging because
            they didn't feed anything from stdin
            """
            if sys.stdin.isatty():
                click.echo(
                    click.style(
                        "Warning: this command reads from stdin but it doesn't appear to be connected to anything. "
                        "Did you forget to pipe from another command?",
                        fg='yellow'),
                    err=True)
            return sys.stdin

        @staticmethod
        def to_test_path(x: TestPathLike) -> TestPath:
            """Convert input to a TestPath"""
            if isinstance(x, str):
                # default representation for a file
                return [{'type': 'file', 'name': x}]
            else:
                return x

        def scan(self, base: str, pattern: str,
                 path_builder: Optional[Callable[[str], Union[TestPath, str, None]]] = None):
            """
            Starting at the 'base' path, recursively add everything that matches the given GLOB pattern

            scan('src/test/java', '**/*.java')

            'path_builder' is a function used to map file name into a custom test path.
            It takes a single string argument that represents the portion matched to the glob pattern,
            and its return value controls what happens to that file:
                - skip a file by returning a False-like object
                - if a str is returned, that's interpreted as a path name and
                  converted to the default test path representation. Typically, `os.path.join(base,file_name)
                - if a TestPath is returned, that's added as is
            """

            if path_builder is None:
                # default implementation of path_builder creates a file name relative to `source` so as not
                # to be affected by the path
                def default_path_builder(file_name):
                    return pathlib.Path(file_path_normalizer.relativize(join(base, file_name))).as_posix()

                path_builder = default_path_builder

            for b in glob.iglob(base):
                for t in glob.iglob(join(b, pattern), recursive=True):
                    if path_builder:
                        path = path_builder(os.path.relpath(t, b))
                    if path:
                        self.test_paths.append(self.to_test_path(path))

        def get_payload(
            self,
            session_id: str,
            target: Optional[PercentageType],
            duration: Optional[DurationType],
            test_runner: str,
        ):
            payload = {
                "testPaths": self.test_paths,
                "testRunner": test_runner,
                "session": {
                    # expecting just the last component, not the whole path
                    "id": os.path.basename(session_id)
                },
                "ignoreNewTests": ignore_new_tests,
                "getTestsFromPreviousSessions": is_get_tests_from_previous_sessions,
            }

            if target is not None:
                payload["goal"] = {
                    "type": "subset-by-percentage",
                    "percentage": target,
                }
            elif duration is not None:
                payload["goal"] = {
                    "type": "subset-by-absolute-time",
                    "duration": duration,
                }
            elif confidence is not None:
                payload["goal"] = {
                    "type": "subset-by-confidence",
                    "percentage": confidence
                }
            else:
                payload['useServerSideOptimizationTarget'] = True

            if ignore_flaky_tests_above:
                payload["dropFlakinessThreshold"] = ignore_flaky_tests_above

            return payload

        def run(self):
            """called after tests are scanned to compute the optimized order"""
            if not is_get_tests_from_previous_sessions and len(self.test_paths) == 0:
                click.echo(
                    click.style(
                        "ERROR: subset candidates are empty. Please set subset candidates or use `--get-tests-from-previous-sessions` option",  # noqa E501
                        fg="red"),
                    err=True)
                exit(1)

            # When Error occurs, return the test name as it is passed.
            original_subset = self.test_paths
            original_rests = []
            summary = {}
            subset_id = ""
            is_brainless = False
            is_observation = False

            if not session_id:
                # Session ID in --session is missing. It might be caused by
                # Launchable API errors.
                pass
            else:
                try:
                    test_runner = context.invoked_subcommand
                    client = LaunchableClient(test_runner=test_runner, dry_run=context.obj.dry_run)

                    # temporarily extend the timeout because subset API response has become slow
                    # TODO: remove this line when API response return respose
                    # within 60 sec
                    timeout = (5, 180)
                    payload = self.get_payload(session_id, target, duration, test_runner)

                    res = client.request("post", "subset", timeout=timeout, payload=payload, compress=True)

                    res.raise_for_status()

                    original_subset = res.json().get("testPaths", [])
                    original_rests = res.json().get("rest", [])
                    subset_id = res.json().get("subsettingId", 0)
                    summary = res.json().get("summary", {})
                    is_brainless = res.json().get("isBrainless", False)
                    is_observation = res.json().get("isObservation", False)

                except Exception as e:
                    if os.getenv(REPORT_ERROR_KEY):
                        raise e
                    else:
                        click.echo(e, err=True)

                    click.echo(click.style(
                        "Warning: the service failed to subset. Falling back to running all tests", fg='yellow'),
                        err=True)

            if len(original_subset) == 0:
                click.echo(click.style("Error: no tests found matching the path.", 'yellow'), err=True)
                return

            if split:
                click.echo("subset/{}".format(subset_id))
            else:
                output_subset, output_rests = original_subset, original_rests

                if is_observation:
                    output_subset = output_subset + output_rests
                    output_rests = []

                if is_output_exclusion_rules:
                    self.exclusion_output_handler(output_subset, output_rests)
                else:
                    self.output_handler(output_subset, output_rests)

            # When Launchable returns an error, the cli skips showing summary
            # report
            if "subset" not in summary.keys() or "rest" not in summary.keys():
                return

            build_name, test_session_id = parse_session(session_id)
            org, workspace = get_org_workspace()

            header = ["", "Candidates",
                      "Estimated duration (%)", "Estimated duration (min)"]
            rows = [
                [
                    "Subset",
                    len(original_subset),
                    summary["subset"].get("rate", 0.0),
                    summary["subset"].get("duration", 0.0),
                ],
                [
                    "Remainder",
                    len(original_rests),
                    summary["rest"].get("rate", 0.0),
                    summary["rest"].get("duration", 0.0),
                ],
                [],
                [
                    "Total",
                    len(original_subset) + len(original_rests),
                    summary["subset"].get("rate", 0.0) + summary["rest"].get("rate", 0.0),
                    summary["subset"].get("duration", 0.0) + summary["rest"].get("duration", 0.0),
                ],
            ]

            if is_brainless:
                click.echo(
                    "Your model is currently in training", err=True)

            click.echo(
                "Launchable created subset {} for build {} (test session {}) in workspace {}/{}".format(
                    subset_id,
                    build_name,
                    test_session_id,
                    org, workspace,
                ), err=True,
            )
            if is_observation:
                click.echo(
                    "(This test session is under observation mode)",
                    err=True)

            click.echo("", err=True)
            click.echo(tabulate(rows, header, tablefmt="github", floatfmt=".2f"), err=True)

            click.echo(
                "\nRun `launchable inspect subset --subset-id {}` to view full subset details".format(subset_id),
                err=True)

    context.obj = Optimize(dry_run=context.obj.dry_run)
