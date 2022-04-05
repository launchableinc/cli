from launchable.commands.record.build import build
from launchable.utils.authentication import get_org_workspace
from launchable.utils.session import parse_session, read_build
import click
import os
import sys
from os.path import join, relpath
import pathlib
import glob
from typing import Callable, Union, Optional, List
from ..utils.click import PERCENTAGE, DURATION, PercentageType, DurationType
from ..utils.env_keys import REPORT_ERROR_KEY
from ..utils.http_client import LaunchableClient
from ..testpath import TestPath, FilePathNormalizer
from .helper import find_or_create_session
from ..utils.click import KeyValueType
from .test_path_writer import TestPathWriter
from tabulate import tabulate
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
    help='output the rest of subset',
    type=str,
)
@click.option(
    "--flavor",
    "flavor",
    help='flavors',
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
    "--no_base_path_inference",
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
):

    session_id = find_or_create_session(context, session, build_name, flavor)
    file_path_normalizer = FilePathNormalizer(
        base_path, no_base_path_inference=no_base_path_inference)

    # TODO: placed here to minimize invasion in this PR to reduce the likelihood of
    # PR merge hell. This should be moved to a top-level class

    TestPathWriter.base_path = base_path

    class Optimize(TestPathWriter):
        # test_paths: List[TestPath]  # doesn't work with Python 3.5

        # Where we take TestPath, we also accept a path name as a string.
        TestPathLike = Union[str, TestPath]

        # output_handler: Callable[[
        #   List[TestPathLike], List[TestPathLike]], None]

        def __init__(self, dry_run=False):
            self.test_paths = []
            self.output_handler = self._default_output_handler
            super(Optimize, self).__init__(dry_run=dry_run)

        def _default_output_handler(self, output, rests):
            # regardless of whether we managed to talk to the service we produce
            # test names
            if rest:
                if len(rests) == 0:
                    rests.append(output[0])

                self.write_file(rest, rests)

            self.print(output)

        def test_path(self, path: TestPathLike):
            def rel_base_path(path):
                if isinstance(path, str):
                    return pathlib.Path(file_path_normalizer.relativize(path)).as_posix()
                else:
                    return path

            if isinstance(path, str) and any(s in path for s in ('*', "?")):
                for i in glob.iglob(path, recursive=True):
                    if os.path.isfile(i):
                        self.test_paths.append(
                            self.to_test_path(rel_base_path(i)))
                return

            """register one test"""
            self.test_paths.append(self.to_test_path(rel_base_path(path)))

        def stdin(self):
            """
            Returns sys.stdin, but after ensuring that it's connected to something reasonable.

            This prevents a typical problem where users think CLI is hanging because
            they didn't feed anything from stdin
            """
            if sys.stdin.isatty():
                click.echo(click.style(
                    "Warning: this command reads from stdin but it doesn't appear to be connected to anything. Did you forget to pipe from another command?",
                    fg='yellow'), err=True)
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

            if path_builder == None:
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

        def get_payload(self, session_id, target, duration):
            payload = {
                "testPaths": self.test_paths,
                "session": {
                    # expecting just the last component, not the whole path
                    "id": os.path.basename(session_id)
                },
                "ignoreNewTests": ignore_new_tests,
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

            return payload

        def run(self):
            """called after tests are scanned to compute the optimized order"""

            # When Error occurs, return the test name as it is passed.
            output = self.test_paths
            rests = []
            summary = {}
            subset_id = ""
            is_brainless = False

            if not session_id:
                # Session ID in --session is missing. It might be caused by Launchable API errors.
                pass
            else:
                try:
                    client = LaunchableClient(
                        test_runner=context.invoked_subcommand,
                        dry_run=context.obj.dry_run)

                    # temporarily extend the timeout because subset API response has become slow
                    # TODO: remove this line when API response return respose within 60 sec
                    timeout = (5, 180)
                    payload = self.get_payload(session_id, target, duration)

                    res = client.request(
                        "post", "subset", timeout=timeout, payload=payload, compress=True)

                    res.raise_for_status()

                    output = res.json()["testPaths"]
                    rests = res.json()["rest"]
                    subset_id = res.json()["subsettingId"]
                    summary = res.json()["summary"]
                    is_brainless = res.json()["isBrainless"]

                except Exception as e:
                    if os.getenv(REPORT_ERROR_KEY):
                        raise e
                    else:
                        click.echo(e, err=True)
                    click.echo(click.style(
                        "Warning: the service failed to subset. Falling back to running all tests", fg='yellow'),
                        err=True)

            if len(output) == 0:
                click.echo(click.style(
                    "Error: no tests found matching the path.", 'yellow'), err=True)
                return

            if split:
                click.echo("subset/{}".format(subset_id))
            else:
                self.output_handler(output, rests)

            # When Launchable returns an error, the cli skips showing summary report
            if "subset" not in summary.keys() or "rest" not in summary.keys():
                return

            build_name, test_session_id = parse_session(session_id)
            org, workspace = get_org_workspace()

            header = ["", "Candidates",
                      "Estimated duration (%)", "Estimated duration (min)"]
            rows = [
                [
                    "Subset",
                    len(output),
                    summary["subset"].get("rate", 0.0),
                    summary["subset"].get("duration", 0.0),
                ],
                [
                    "Remainder",
                    len(rests),
                    summary["rest"].get("rate", 0.0),
                    summary["rest"].get("duration", 0.0),
                ],
                [],
                [
                    "Total",
                    len(output) + len(rests),
                    summary["subset"].get("rate", 0.0) +
                    summary["rest"].get("rate", 0.0),
                    summary["subset"].get("rate", 0.0) +
                    summary["rest"].get("duration", 0.0),
                ],
            ]

            if is_brainless:
                click.echo(
                    "Your model is currently in training", err=True)

            click.echo(
                "Launchable created subset {} for build {} (test session {}) in workspace {}/{}\n".format(subset_id, build_name, test_session_id, org, workspace), err=True)

            click.echo(tabulate(rows, header, tablefmt="github"), err=True)

            click.echo(
                "\nRun `launchable inspect subset --subset-id {}` to view full subset details".format(subset_id), err=True)

    context.obj = Optimize(dry_run=context.obj.dry_run)
