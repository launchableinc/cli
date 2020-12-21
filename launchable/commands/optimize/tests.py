import click
import json
import os
import glob
from typing import Callable
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.http_client import LaunchableClient
from ...utils.token import parse_token


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
    required=True,
    type=int,
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
        def __init__(self):
            self.test_paths = []
            self._formatter = lambda x: x

        @property
        def formatter(self) -> Callable[[str], str]:
            """
            This function, if supplied, is used to format test names
            from the format Launchable uses to the format test runners expect.
            """
            return self._formatter

        @formatter.setter
        def formatter(self, v):
            self._formatter = v

        def test_path(self, name):
            """register one test"""
            self.test_paths.append(name)

        def scan(self, base, pattern, filter=(lambda x: x)):
            """
            Starting at the 'base' path, recursively add everything that matches the given GLOB pattern

            scan('src/test/java', '**/*.java')

            'filter' argument can be used to:
                - post-process the matching file names, by returning a string, or
                - skip items by returning a False-like object
            """
            for t in glob.iglob(os.path.join(base, pattern), recursive=True):
                t = t[len(base)+1:]  # drop the base portion
                t = filter(t)
                if t:
                    self.test_paths({ 'type': 'file', 'name': t})

        def run(self):
            """called after tests are scanned to compute the optimized order"""

            # When Error occurs, return the test name as it is passed.
            # TODO: 
            output = [test_path[0]["name"] for test_path in self.test_paths]

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

                output = res.json()["testNames"]
            except Exception as e:
                if os.getenv(REPORT_ERROR_KEY):
                    raise e
                else:
                    click.echo(e, err=True)

            for t in output:
                click.echo(self.formatter(t))

    context.obj = Optimize()
