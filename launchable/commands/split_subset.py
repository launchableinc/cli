import os
from typing import List, Optional

import click

from ..utils.click import FRACTION, FractionType
from ..utils.env_keys import REPORT_ERROR_KEY
from ..utils.http_client import LaunchableClient
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
    'bin_target',
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
@click.option(
    "--same-bin",
    'same_bin_files',
    help="(Advanced) gather specified tests into same bin",
    type=click.Path(),
    multiple=True,
)
@click.pass_context
def split_subset(
        context: click.core.Context,
        subset_id: str,
        bin_target: FractionType,
        rest: str,
        base_path: str,
        same_bin_files: Optional[List[str]],
):
    TestPathWriter.base_path = base_path

    class SplitSubset(TestPathWriter):
        def __init__(self, dry_run: bool = False):
            super(SplitSubset, self).__init__(dry_run=dry_run)

        def run(self):
            index = bin_target[0]
            count = bin_target[1]

            if (index == 0 or count == 0):
                click.echo(
                    click.style(
                        'Error: invalid bin value. Make sure to set over 0 like `--bin 1/2` but set `--bin {}`'.format(
                            bin_target),
                        'yellow'),
                    err=True,
                )
                return

            if count < index:
                click.echo(
                    click.style(
                        'Error: invalid bin value. Make sure to set below 1 like `--bin 1/2`, `--bin 2/2` but set `--bin {}`'.format(
                            bin_target),
                        'yellow'),
                    err=True,
                )
                return

            output = []
            rests = []
            is_observation = False

            try:
                client = LaunchableClient(
                    test_runner=context.invoked_subcommand,
                    dry_run=context.obj.dry_run)

                payload = {
                    "sliceCount": count,
                    "sliceIndex": index,
                    "sameBins": [],
                }

                tests_in_files = []

                if same_bin_files is not None and len(same_bin_files) > 0:
                    if self.same_bin_formatter is None:
                        raise ValueError("--same-bin option is supported only for gradle test and go-test. "
                                         "Please remove --same-bin option for the other test runner.")
                    same_bins = []
                    for same_bin_file in same_bin_files:
                        with open(same_bin_file, "r") as f:
                            """
                            A same_bin_file expects to have a list of tests with one test per line.
                            Each line of test gets formatted and packed to sameBins list in payload.
                            E.g.
                                For gradle:
                                ```
                                $ cat same_bin_file.txt
                                example.AddTest
                                example.DivTest
                                example.SubTest
                                ```
                                Formatted:
                                ```
                                "sameBins" [
                                    [
                                        [{"type": "class", "name": "example.AddTest"}],
                                        [{"type": "class", "name": "example.DivTest"}],
                                        [{"type": "class", "name": "example.SubTest"}]
                                    ]
                                ]
                                ```
                            E.g.
                                For gotest:
                                ```
                                $ cat same_bin_file.txt
                                example.BenchmarkGreeting
                                example.ExampleGreeting
                                ```
                                Formatted:
                                ```
                                "sameBins" [
                                    [
                                        [
                                            {"type": "class", "name": "example"},
                                            {"type": "testcase", "name": "BenchmarkGreeting"}
                                        ],
                                        [
                                            {"type": "class", "name": "example"},
                                            {"type": "testcase", "name": "ExampleGreeting"}
                                        ]
                                    ]
                                ]
                                ```
                            """
                            tests = f.readlines()
                            # make a list to set to remove duplicate.
                            tests = list(set([s.strip() for s in tests]))
                            for tests_in_file in tests_in_files:
                                for test in tests:
                                    if test in tests_in_file:
                                        raise ValueError(
                                            "Error: you cannot have one test, {}, in multiple same-bins.".format(test))
                            tests_in_files.append(tests)
                            test_data = [
                                self.same_bin_formatter(s) for s in tests]
                            same_bins.append(test_data)

                    payload["sameBins"] = same_bins

                res = client.request(
                    "POST", "{}/slice".format(subset_id), payload=payload)
                res.raise_for_status()

                output = res.json()["testPaths"]
                rests = res.json()["rest"]
                is_observation = res.json().get("isObservation", False)

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

            if is_observation:
                output = output + rests
            if rest:
                if len(rests) == 0:
                    rests.append(output[0])

                self.write_file(rest, rests)

            self.print(output)

    context.obj = SplitSubset(dry_run=context.obj.dry_run)
