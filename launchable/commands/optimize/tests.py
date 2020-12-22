import click
import json
import os
import glob
from typing import Callable, List, Union
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.http_client import LaunchableClient
from ...utils.token import parse_token
from ...testpath import TestPath


@click.group(help="Subsetting tests")
@click.option(
    '--target',
    'target',
    help='subsetting target percentage 0.0-1.0',
    required=True,
    type=float,
    default=0.8,
)
@click.option(
    '--session',
    'session_id',
    help='Test session ID',
    type=int,
    required=os.getenv(REPORT_ERROR_KEY),  # validate session_id under debug mode
)
@click.option(
    '--source',
    help='repository district'
         'REPO_DIST like --source . ',
    metavar="REPO_NAME",
)
@click.option(
    '--name',
    'build_name',
    help='build identifier',
    required=True,
    type=str,
    metavar='BUILD_ID'
)
@click.pass_context
def tests(context, target, session_id, source, build_name):
    token, org, workspace = parse_token()

    # TODO: placed here to minimize invasion in this PR to reduce the likelihood of
    # PR merge hell. This should be moved to a top-level class
    class Optimize:
        # test_paths: List[TestPath]  # doesn't work with Python 3.5

        # Where we take TestPath, we also accept a path name as a string.
        TestPathLike = Union[str,TestPath]

        def __init__(self):
            self.test_paths = []
            # default formatter t hat's in line with to_test_path(str)
            # TODO: robustness improvement.
            self._formatter = lambda x: x[0]['name']

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

        def test_path(self, path: TestPathLike):
            """register one test"""
            self.test_paths.append(self.to_test_path(path))

        @staticmethod
        def to_test_path(x: TestPathLike) -> TestPath:
            """Convert input to a TestPath"""
            if isinstance(x, str):
                # default representation for a file
                return [{'type': 'file', 'name': x}]
            else:
                return x

        def scan(self, base: str, pattern: str, path_builder: Callable[[str], Union[TestPath, str, None]] = lambda x:x):
            """
            Starting at the 'base' path, recursively add everything that matches the given GLOB pattern

            scan('src/test/java', '**/*.java')

            'path_builder' argument is used to map file name into a custom test path:
                - skip a file by returning a False-like object
                - if a str is returned, that's interpreted as a path name and
                  converted to the default test path representation
                - if a TestPath is returned, that's added as is
            """
            for t in glob.iglob(os.path.join(base, pattern), recursive=True):
                t = t[len(base) + 1:]  # drop the base portion
                t = path_builder(t)
                if t:
                    self.test_paths.append(self.to_test_path(t))

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
                    }

                    payload = {
                        "testPaths": self.test_paths,
                        "target": target,
                        "session": {
                            "id": session_id
                        }
                    }

                    path = "/intake/organizations/{}/workspaces/{}/subset".format(
                        org, workspace)

                    client = LaunchableClient(token)
                    res = client.request("post", path, data=json.dumps(
                        payload).encode(), headers=headers)
                    res.raise_for_status()

                    output = res.json()["testPaths"]
                except Exception as e:
                    if os.getenv(REPORT_ERROR_KEY):
                        raise e
                    else:
                        click.echo(e, err=True)

            # regardless of whether we managed to talk to the service
            # we produce test names
            for t in output:
                click.echo(self.formatter(t))

    context.obj = Optimize()
