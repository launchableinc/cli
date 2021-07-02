import click
import os
from typing import Union, Callable

from ..testpath import TestPath
from ..utils.env_keys import REPORT_ERROR_KEY
from ..utils.http_client import LaunchableClient


@click.group(help="Split subsetting tests")
@click.option(
    '--subset-id',
    'subset_id',
    help='subset id',
    type=str,
    required=True,
)
@click.option(
    '--bin',
    'bin',
    help='bin',
    type=str,
    required=True
)
@click.option(
    '--rest',
    'rest',
    help='output the rest of subset',
    type=str,
)
@click.option(
    '--base',
    'base_path',
    help='(Advanced) base directory to make test names portable',
    type=click.Path(exists=True, file_okay=False),
    metavar="DIR",
)
@click.pass_context
def split_subset(context, subset_id,  bin: str, rest: str, base_path: str):
    class SplitSubset():
        TestPathLike = Union[str, TestPath]

        def __init__(self):
            self._formatter = ""
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

        def run(self):
            b = bin.strip().split('/')
            if (len(b) != 2):
                click.echo(click.style(
                    'Error: invalid format. Make sure to set like `--bin 1/2` but set `--bin {}`'.format(bin), 'yellow'), err=True)
                return

            index = int(b[0])
            count = int(b[1])

            if (index == 0 or count == 0):
                click.echo(click.style(
                    'Error: invalid bin value. Make sure to set over 0 like `--bin 1/2` but set `--bin {}`'.format(bin), 'yellow'), err=True)
                return

            if count < index:
                click.echo(click.style(
                    'Error: invalid bin value. Make sure to set below 1 like `--bin 1/2`, `--bin 2/2` but set `--bin {}`'.format(bin), 'yellow'), err=True)
                return

            output = []
            rests = []

            try:
                client = LaunchableClient(
                    test_runner=context.invoked_subcommand)

                payload = {
                    "sliceCount": count,
                    "sliceIndex": index,
                }

                res = client.request("POST", subset_id, payload=payload)

                res.raise_for_status()

                output = res.json()["testPaths"]
                rests = res.json()["rest"]

            except Exception as e:
                if os.getenv(REPORT_ERROR_KEY):
                    raise e
                else:
                    click.echo(e, err=True)
                    click.echo(click.style(
                        "Warning: the service failed to subset. Falling back to running all tests", fg='yellow'),
                        err=True)
                    return

            if rest:
                if len(rests) == 0:
                    # no tests will be in the "rest" file. but add a test case to avoid failing tests using this
                    rests.append(self.formatter(output[0]))

                open(rest, "w+", encoding="utf-8").write(
                    self.separator.join(self.formatter(t) for t in rests))

            click.echo(self.separator.join(self.formatter(t)
                                           for t in output))

    context.obj = SplitSubset()
