import click
import os

from ..utils.env_keys import REPORT_ERROR_KEY
from ..utils.http_client import LaunchableClient
from ..utils.click import FRACTION
from .test_path_writer import TestPathWriter


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
    type=FRACTION,
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
def split_subset(context, subset_id: str,  bin, rest: str, base_path: str):

    TestPathWriter.base_path = base_path

    class SplitSubset(TestPathWriter):
        def __init__(self):
            super(SplitSubset, self).__init__()

        def run(self):
            index = bin[0]
            count = bin[1]

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

                res = client.request(
                    "POST", "{}/slice".format(subset_id), payload=payload)
                res.raise_for_status()

                output = res.json()["testPaths"]
                rests = res.json()["rest"]

            except Exception as e:
                if os.getenv(REPORT_ERROR_KEY):
                    raise e
                else:
                    click.echo(e, err=True)
                    click.echo(click.style(
                        "Warning: the service failed to split subset. Falling back to running all tests", fg='yellow'),
                        err=True)
                    return

            if len(output) == 0:
                click.echo(click.style(
                    "Error: no tests found in this subset id.", 'yellow'), err=True)
                return

            if rest:
                if len(rests) == 0:
                    rests.append(output[0])

                self.write_file(rest, rests)

            self.print(output)

    context.obj = SplitSubset()
