import click
import json
import os
import sys
from os.path import *
import glob
import gzip
from typing import Callable, Union, Optional
from ..utils.click import PERCENTAGE
from ..utils.env_keys import REPORT_ERROR_KEY
from ..utils.http_client import LaunchableClient
from ..utils.token import parse_token
from ..testpath import TestPath
from ..utils.session import read_session
from .record.session import session

# TODO: rename files and function accordingly once the PR landscape


@click.group(help="Subsetting tests")
@click.option(
    '--target',
    'target',
    help='subsetting target from 0% to 100%',
    required=True,
    type=PERCENTAGE,
)
@click.option(
    '--session',
    'session_id',
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
    metavar='BUILD_NAME'
)
@click.pass_context
def subset(context, target, session_id, base_path: str, build_name: str):
    token, org, workspace = parse_token()

    if session_id and build_name:
        raise click.UsageError(
            'Only one of --build or --session should be specified')

    if not session_id:
        if build_name:
            session_id = read_session(build_name)
            if not session_id:
                context.invoke(session, build_name=build_name, save_session_file=True, print_session=False)
                session_id = read_session(build_name)
        else:
            raise click.UsageError(
                'Either --build or --session has to be specified')

    # TODO: placed here to minimize invasion in this PR to reduce the likelihood of
    # PR merge hell. This should be moved to a top-level class
    class Optimize:
        # test_paths: List[TestPath]  # doesn't work with Python 3.5

        # Where we take TestPath, we also accept a path name as a string.
        TestPathLike = Union[str, TestPath]

        def __init__(self):
            self.test_paths = []
            # TODO: robustness improvement.
            self._formatter = Optimize.default_formatter
            self._separator = "\n"

        @staticmethod
        def default_formatter(x: TestPath):
            """default formatter that's in line with to_test_path(str)"""
            file_name = x[0]['name']
            if base_path:
                # default behavior consistent with default_path_builder's relative path handling
                file_name = join(base_path, file_name)
            return file_name

        @property
        def formatter(self) -> Callable[[TestPath], str]:
            """
            This function, if supplied, is used to format test names
            from the format Launchable uses to the format test runners expect.
            """
            return self._formatter

        @formatter.setter
        def formatter(self, v: Callable[[TestPath], str]):
            self._formatter = v

        @property
        def separator(self) -> str:
            return self._separator

        @separator.setter
        def separator(self, s: str):
            self._separator = s

        def test_path(self, path: TestPathLike):
            """register one test"""
            self.test_paths.append(self.to_test_path(path))

        def stdin(self):
            """
            Returns sys.stdin, but after ensuring that it's connected to something reasonable.

            This prevents a typical problem where users think CLI is hanging because
            they didn't feed anything from stdin
            """
            if sys.stdin.isatty():
                click.echo(click.style("Warning: this command reads from stdin but it doesn't appear to be connected to anything. Did you forget to pipe from another command?", fg='yellow'), err=True)
            return sys.stdin

        @staticmethod
        def to_test_path(x: TestPathLike) -> TestPath:
            """Convert input to a TestPath"""
            if isinstance(x, str):
                # default representation for a file
                return [{'type': 'file', 'name': x}]
            else:
                return x

        def scan(self, base: str, pattern: str, path_builder: Optional[Callable[[str], Union[TestPath, str, None]]] = None):
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
                    file_name = join(base, file_name)
                    if base_path:
                        # relativize against `base_path` to make the path name portable
                        file_name = normpath(
                            relpath(file_name, start=base_path))
                    return file_name
                path_builder = default_path_builder

            for t in glob.iglob(join(base, pattern), recursive=True):
                if path_builder:
                    path = path_builder(t[len(base)+1:])
                    if path:
                        self.test_paths.append(self.to_test_path(path))

        def run(self):
            """called after tests are scanned to compute the optimized order"""

            # When Error occurs, return the test name as it is passed.
            output = self.test_paths

            if not session_id:
                # Session ID in --session is missing. It might be caused by Launchable API errors.
                pass
            else:
                try:
                    headers = {
                        "Content-Type": "application/json",
                        "Content-Encoding": "gzip",
                    }

                    payload = {
                        "testPaths": self.test_paths,
                        "target": target,
                        "session": {
                            # expecting just the last component, not the whole path
                            "id": os.path.basename(session_id)
                        }
                    }

                    path = "/intake/organizations/{}/workspaces/{}/subset".format(
                        org, workspace)

                    client = LaunchableClient(token)
                    # temporarily extend the timeout because subset API response has become slow
                    # TODO: remove this line when API response return respose within 60 sec
                    timeout = (5, 180)
                    res = client.request("post", path, data=gzip.compress(json.dumps(
                        payload).encode()), headers=headers, timeout=timeout)
                    res.raise_for_status()

                    output = res.json()["testPaths"]
                except Exception as e:
                    if os.getenv(REPORT_ERROR_KEY):
                        raise e
                    else:
                        click.echo(e, err=True)
                    click.echo(click.style("Warning: the service failed to subset. Falling back to running all tests", fg='yellow'), err=True)


            # regardless of whether we managed to talk to the service
            # we produce test names
            click.echo(self.separator.join(self.formatter(t) for t in output))

    context.obj = Optimize()
