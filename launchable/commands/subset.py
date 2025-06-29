import glob
import json
import os
import pathlib
import sys
from multiprocessing import Process
from os.path import join
from typing import Any, Callable, Dict, List, Optional, Sequence, TextIO, Tuple, Union

import click
from tabulate import tabulate

from launchable.utils.authentication import get_org_workspace
from launchable.utils.session import parse_session
from launchable.utils.tracking import Tracking, TrackingClient

from ..app import Application
from ..testpath import FilePathNormalizer, TestPath
from ..utils.click import DURATION, KEY_VALUE, PERCENTAGE, DurationType, PercentageType, ignorable_error
from ..utils.commands import Command
from ..utils.env_keys import REPORT_ERROR_KEY
from ..utils.fail_fast_mode import (FailFastModeValidateParams, fail_fast_mode_validate,
                                    set_fail_fast_mode, warn_and_exit_if_fail_fast_mode)
from ..utils.launchable_client import LaunchableClient
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
    '--goal-spec',
    'goal_spec',
    help='subsetting by programmatic goal definition',
    type=str,
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
    type=KEY_VALUE,
    default=(),
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
    "--non-blocking",
    "is_non_blocking",
    help="Do not wait for subset requests in observation mode.",
    is_flag=True,
    hidden=True,
)
@click.option(
    "--ignore-flaky-tests-above",
    "ignore_flaky_tests_above",
    help='Ignore flaky tests above the value set by this option. You can confirm flaky scores in WebApp',
    type=click.FloatRange(min=0, max=1.0),
)
@click.option(
    '--link',
    'links',
    help="Set external link of title and url",
    multiple=True,
    default=(),
    type=KEY_VALUE,
)
@click.option(
    "--no-build",
    "is_no_build",
    help="If you want to only send test reports, please use this option",
    is_flag=True,
)
@click.option(
    '--session-name',
    'session_name',
    help='test session name',
    required=False,
    type=str,
    metavar='SESSION_NAME',
)
@click.option(
    '--lineage',
    'lineage',
    help='Set lineage name. This option value will be passed to the record session command if a session isn\'t created yet.',
    required=False,
    type=str,
    metavar='LINEAGE',
)
@click.option(
    "--prioritize-tests-failed-within-hours",
    "prioritize_tests_failed_within_hours",
    help="Prioritize tests that failed within the specified hours; maximum 720 hours (= 24 hours * 30 days)",
    type=click.IntRange(min=0, max=24 * 30),
)
@click.option(
    "--prioritized-tests-mapping",
    "prioritized_tests_mapping_file",
    help='Prioritize tests based on test mapping file',
    required=False,
    type=click.File('r'),
)
@click.option(
    '--test-suite',
    'test_suite',
    help='Set test suite name. This option value will be passed to the record session command if a session isn\'t created yet.',  # noqa: E501
    required=False,
    type=str,
    metavar='TEST_SUITE',
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
    flavor: Sequence[Tuple[str, str]],
    confidence: Optional[PercentageType],
    goal_spec: Optional[str],
    split: bool,
    no_base_path_inference: bool,
    ignore_new_tests: bool,
    is_observation: bool,
    is_get_tests_from_previous_sessions: bool,
    is_output_exclusion_rules: bool,
    is_non_blocking: bool,
    ignore_flaky_tests_above: Optional[float],
    links: Sequence[Tuple[str, str]] = (),
    is_no_build: bool = False,
    session_name: Optional[str] = None,
    lineage: Optional[str] = None,
    prioritize_tests_failed_within_hours: Optional[int] = None,
    prioritized_tests_mapping_file: Optional[TextIO] = None,
    test_suite: Optional[str] = None,
):
    app = context.obj
    tracking_client = TrackingClient(Command.SUBSET, app=app)
    client = LaunchableClient(
        test_runner=context.invoked_subcommand,
        app=app,
        tracking_client=tracking_client)

    set_fail_fast_mode(client.is_fail_fast_mode())
    fail_fast_mode_validate(FailFastModeValidateParams(
        command=Command.SUBSET,
        session=session,
        build=build_name,
        flavor=flavor,
        is_observation=is_observation,
        links=links,
        is_no_build=is_no_build,
        test_suite=test_suite,
    ))

    if is_observation and is_output_exclusion_rules:
        msg = (
            "WARNING: --observation and --output-exclusion-rules are set. "
            "No output will be generated."
        )
        click.echo(
            click.style(
                msg,
                fg="yellow"),
            err=True,
        )
        tracking_client.send_error_event(
            event_name=Tracking.ErrorEvent.WARNING_ERROR,
            stack_trace=msg
        )

    if prioritize_tests_failed_within_hours is not None and prioritize_tests_failed_within_hours > 0:
        if ignore_new_tests or (ignore_flaky_tests_above is not None and ignore_flaky_tests_above > 0):
            msg = (
                "Cannot use --ignore-new-tests or --ignore-flaky-tests-above options "
                "with --prioritize-tests-failed-within-hours"
            )
            click.echo(
                click.style(
                    msg,
                    fg="red"),
                err=True,
            )
            tracking_client.send_error_event(
                event_name=Tracking.ErrorEvent.INTERNAL_CLI_ERROR,
                stack_trace=msg,
            )
            sys.exit(1)

    if is_no_build and session:
        warn_and_exit_if_fail_fast_mode(
            "WARNING: `--session` and `--no-build` are set.\nUsing --session option value ({}) and ignoring `--no-build` option".format(session))  # noqa: E501
        is_no_build = False

    session_id = None

    try:
        if session_name:
            if not build_name:
                raise click.UsageError(
                    '--build option is required when you use a --session-name option ')
            sub_path = "builds/{}/test_session_names/{}".format(build_name, session_name)
            client = LaunchableClient(test_runner=context.invoked_subcommand, app=context.obj, tracking_client=tracking_client)
            res = client.request("get", sub_path)
            res.raise_for_status()
            session_id = "builds/{}/test_sessions/{}".format(build_name, res.json().get("id"))
        else:
            session_id = find_or_create_session(
                context=context,
                session=session,
                build_name=build_name,
                flavor=flavor,
                is_observation=is_observation,
                links=links,
                is_no_build=is_no_build,
                lineage=lineage,
                tracking_client=tracking_client,
                test_suite=test_suite,
            )
    except click.UsageError as e:
        click.echo(
            click.style(
                str(e),
                fg="red"),
            err=True,
        )
        tracking_client.send_error_event(event_name=Tracking.ErrorEvent.USER_ERROR, stack_trace=str(e))
        sys.exit(1)
    except Exception as e:
        tracking_client.send_error_event(
            event_name=Tracking.ErrorEvent.INTERNAL_CLI_ERROR,
            stack_trace=str(e),

        )
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            click.echo(ignorable_error(e), err=True)

    if is_non_blocking:
        if (not is_observation) and session_id:
            try:
                client = LaunchableClient(
                    app=app,
                    tracking_client=tracking_client)
                res = client.request("get", session_id)
                is_observation_in_recorded_session = res.json().get("isObservation", False)
                if not is_observation_in_recorded_session:
                    msg = "You have to specify --observation option to use non-blocking mode"
                    click.echo(
                        click.style(
                            msg,
                            fg="red"),
                        err=True,
                    )
                    tracking_client.send_error_event(
                        event_name=Tracking.ErrorEvent.INTERNAL_CLI_ERROR,
                        stack_trace=msg,
                    )
                    sys.exit(1)
            except Exception as e:
                tracking_client.send_error_event(
                    event_name=Tracking.ErrorEvent.INTERNAL_CLI_ERROR,
                    stack_trace=str(e),
                )
                click.echo(ignorable_error(e), err=True)

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

        def __init__(self, app: Application):
            self.rest = rest
            self.input_given = False  # set to True when an attempt was made to add to self.test_paths
            self.test_paths: List[List[Dict[str, str]]] = []
            self.output_handler = self._default_output_handler
            self.exclusion_output_handler = self._default_exclusion_output_handler
            self.is_get_tests_from_previous_sessions = is_get_tests_from_previous_sessions
            self.is_output_exclusion_rules = is_output_exclusion_rules
            super(Optimize, self).__init__(app=app)

        def _default_output_handler(self, output: List[TestPath], rests: List[TestPath]):
            if rest:
                self.write_file(rest, rests)

            if output:
                self.print(output)

        def _default_exclusion_output_handler(self, subset: List[TestPath], rest: List[TestPath]):
            self.output_handler(rest, subset)

        def test_path(self, path: TestPathLike):
            """register one test"""

            def rel_base_path(path):
                if isinstance(path, str):
                    return pathlib.Path(file_path_normalizer.relativize(path)).as_posix()
                else:
                    return path

            self.input_given = True
            if isinstance(path, str) and any(s in path for s in ('*', "?")):
                for i in glob.iglob(path, recursive=True):
                    if os.path.isfile(i):
                        self.test_paths.append(self.to_test_path(rel_base_path(i)))
            else:
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
                warn_and_exit_if_fail_fast_mode(
                    "Warning: this command reads from stdin but it doesn't appear to be connected to anything. "
                    "Did you forget to pipe from another command?"
                )
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

            self.input_given = True

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
            payload: Dict[str, Any] = {
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
            elif goal_spec is not None:
                payload["goal"] = {
                    "type": "subset-by-goal-spec",
                    "goal": goal_spec
                }
            else:
                payload['useServerSideOptimizationTarget'] = True

            if ignore_flaky_tests_above:
                payload["dropFlakinessThreshold"] = ignore_flaky_tests_above

            if prioritize_tests_failed_within_hours:
                payload["hoursToPrioritizeFailedTest"] = prioritize_tests_failed_within_hours

            if prioritized_tests_mapping_file:
                payload['prioritizedTestsMapping'] = json.load(prioritized_tests_mapping_file)

            return payload

        def run(self):
            """called after tests are scanned to compute the optimized order"""
            if not is_get_tests_from_previous_sessions and len(self.test_paths) == 0:
                if self.input_given:
                    msg = "ERROR: Given arguments did not match any tests. They appear to be incorrect/non-existent."  # noqa E501
                else:
                    msg = "ERROR: Expecting tests to be given, but none provided. See https://www.launchableinc.com/docs/features/predictive-test-selection/requesting-and-running-a-subset-of-tests/subsetting-with-the-launchable-cli/ and provide ones, or use the `--get-tests-from-previous-sessions` option"  # noqa E501
                click.echo(click.style(msg, fg="red"), err=True)
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

                    # temporarily extend the timeout because subset API response has become slow
                    # TODO: remove this line when API response return respose
                    # within 300 sec
                    timeout = (5, 300)
                    payload = self.get_payload(session_id, target, duration, test_runner)

                    if is_non_blocking:
                        # Create a new process for requesting a subset.
                        process = Process(target=subset_request, args=(client, timeout, payload))
                        process.start()
                        click.echo("The subset was requested in non-blocking mode.", err=True)
                        self.output_handler(self.test_paths, [])
                        return

                    res = subset_request(client=client, timeout=timeout, payload=payload)

                    # The status code 422 is returned when validation error of the test mapping file occurs.
                    if res.status_code == 422:
                        msg = "Error: {}".format(res.reason)
                        tracking_client.send_error_event(
                            event_name=Tracking.ErrorEvent.USER_ERROR,
                            stack_trace=msg,
                        )
                        click.echo(
                            click.style(msg, fg="red"),
                            err=True)
                        sys.exit(1)

                    res.raise_for_status()

                    original_subset = res.json().get("testPaths", [])
                    original_rests = res.json().get("rest", [])
                    subset_id = res.json().get("subsettingId", 0)
                    summary = res.json().get("summary", {})
                    is_brainless = res.json().get("isBrainless", False)
                    is_observation = res.json().get("isObservation", False)

                except Exception as e:
                    tracking_client.send_error_event(
                        event_name=Tracking.ErrorEvent.INTERNAL_CLI_ERROR,
                        stack_trace=str(e),
                    )

                    client.print_exception_and_recover(
                        e, "Warning: the service failed to subset. Falling back to running all tests")

            if len(original_subset) == 0:
                warn_and_exit_if_fail_fast_mode("Error: no tests found matching the path.")
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

    context.obj = Optimize(app=context.obj)


def subset_request(client: LaunchableClient, timeout: Tuple[int, int], payload: Dict[str, Any]):
    return client.request("post", "subset", timeout=timeout, payload=payload, compress=True)
