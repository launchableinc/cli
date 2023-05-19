import os
from typing import List, Optional

import click

from launchable.testpath import TestPath

from ..utils.click import FRACTION, FractionType
from ..utils.env_keys import REPORT_ERROR_KEY
from ..utils.http_client import LaunchableClient
from .test_path_writer import TestPathWriter

SPLIT_BY_GROUPS_NO_GROUP_NAME = "nogroup"
SPLIT_BY_GROUP_SUBSET_GROUPS_FILE_NAME = "subset-groups.txt"
SPLIT_BY_GROUP_REST_GROUPS_FILE_NAME = "rest-groups.txt"


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
@click.option(
    "--split-by-groups",
    'is_split_by_groups',
    help="split by groups that were set by `launchable record tests --group`",
    is_flag=True
)
@click.option(
    "--split-by-groups-with-rest",
    'is_split_by_groups_with_rest',
    help="split by groups that were set by `launchable record tests --group` and produces with rest files",
    is_flag=True
)
@click.option(
    "--split-by-groups-output-dir",
    'split_by_groups_output_dir',
    type=click.Path(file_okay=False),
    default=os.getcwd(),
    help="split results output dir",
)
@click.option(
    "--output-exclusion-rules",
    "is_output_exclusion_rules",
    help="outputs the exclude test list. Switch the subset and rest.",
    is_flag=True,
)
@click.pass_context
def split_subset(
        context: click.core.Context,
        subset_id: str,
        bin_target: FractionType,
        rest: str,
        base_path: str,
        same_bin_files: Optional[List[str]],
        is_split_by_groups: bool,
        is_split_by_groups_with_rest: bool,
        split_by_groups_output_dir: click.Path,
        is_output_exclusion_rules: bool,
):
    if len(subset_id.split("/")) != 2:
        click.echo(
            click.style('Error: subset ID cannot be empty. It should be passed with `subset/<subset id>` format.',
                        'yellow'),
            err=True,
        )
        return

    TestPathWriter.base_path = base_path

    client = LaunchableClient(test_runner=context.invoked_subcommand, dry_run=context.obj.dry_run)

    class SplitSubset(TestPathWriter):
        def __init__(self, dry_run: bool = False):
            super(SplitSubset, self).__init__(dry_run=dry_run)
            self.rest = rest
            self.output_handler = self._default_output_handler
            self.exclusion_output_handler = self._default_exclusion_output_handler
            self.split_by_groups_output_handler = self._default_split_by_groups_output_handler
            self.split_by_groups_exclusion_output_handler = self._default_split_by_groups_exclusion_output_handler
            self.is_split_by_groups_with_rest = is_split_by_groups_with_rest
            self.split_by_groups_output_dir = split_by_groups_output_dir
            self.is_output_exclusion_rules = is_output_exclusion_rules

        def _default_output_handler(self, output: List[TestPath], rests: List[TestPath]):
            if rest:
                self.write_file(rest, rests)

            if output:
                self.print(output)

        def _default_exclusion_output_handler(self, subset: List[TestPath], rest: List[TestPath]):
            self.output_handler(rest, subset)

        def _default_split_by_groups_output_handler(self, group_name: str, subset: List[TestPath], rests: List[TestPath]):
            if is_split_by_groups_with_rest:
                self.write_file("{}/rest-{}.txt".format(split_by_groups_output_dir, group_name), rests)

            if len(subset) > 0:
                self.write_file("{}/subset-{}.txt".format(split_by_groups_output_dir, group_name), subset)

        def _default_split_by_groups_exclusion_output_handler(
                self, group_name: str, subset: List[TestPath],
                rests: List[TestPath]):
            self.split_by_groups_output_handler(group_name, rests, subset)

        def _is_split_by_groups(self) -> bool:
            return is_split_by_groups or is_split_by_groups_with_rest

        def split_by_bin(self):
            index, count = 0, 0
            if not is_split_by_groups:
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
                            'Error: invalid bin value. Make sure to set below 1 like `--bin 1/2`, `--bin 2/2` '
                            'but set `--bin {}`'.format(bin_target),
                            'yellow'),
                        err=True,
                    )
                    return

            output_subset = []
            output_rests = []
            is_observation = False

            try:
                payload = {
                    "sliceCount": count,
                    "sliceIndex": index,
                    "sameBins": [],
                    "splitByGroups": is_split_by_groups
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
                            test_data = [self.same_bin_formatter(s) for s in tests]
                            same_bins.append(test_data)

                    payload["sameBins"] = same_bins

                res = client.request("POST", "{}/slice".format(subset_id), payload=payload)
                res.raise_for_status()

                output_subset = res.json().get("testPaths", [])
                output_rests = res.json().get("rest", [])
                is_observation = res.json().get("isObservation", False)

                if len(output_subset) == 0:
                    click.echo(click.style(
                        "Error: no tests found for this subset id.", 'yellow'), err=True)
                    return

                if is_observation:
                    output_subset = output_subset + output_rests
                    output_rests = []

                if is_output_exclusion_rules:
                    self.exclusion_output_handler(output_subset, output_rests)
                else:
                    self.output_handler(output_subset, output_rests)

            except Exception as e:
                if os.getenv(REPORT_ERROR_KEY):
                    raise e
                else:
                    click.echo(e, err=True)
                    click.echo(click.style(
                        "Warning: the service failed to split subset. Falling back to running all tests", fg='yellow'),
                        err=True)
                    return

        def _write_split_by_groups_group_names(self, subset_group_names: List[str], rest_group_names: List[str]):
            if is_output_exclusion_rules:
                subset_group_names, rest_group_names = rest_group_names, subset_group_names

            if len(subset_group_names) > 0:
                with open("{}/{}".format(split_by_groups_output_dir, SPLIT_BY_GROUP_SUBSET_GROUPS_FILE_NAME),
                          "w+", encoding="utf-8") as f:
                    f.write("\n".join(subset_group_names))

            if is_split_by_groups_with_rest:
                with open("{}/{}".format(split_by_groups_output_dir, SPLIT_BY_GROUP_REST_GROUPS_FILE_NAME),
                          "w+", encoding="utf-8") as f:
                    f.write("\n".join(rest_group_names))

        def split_by_group_names(self):
            try:
                res = client.request("POST", "{}/split-by-groups".format(subset_id))
                res.raise_for_status()

                is_observation = res.json().get("isObservation", False)
                split_groups = res.json().get("splitGroups", [])

                subset_group_names = []
                rest_group_names = []

                for group in split_groups:
                    group_name = group.get("groupName", "")
                    subset = group.get("subset", [])
                    rests = group.get("rest", [])

                    if is_observation:
                        subset, rests = subset + rests, []

                    if len(subset) > 0 and group_name != SPLIT_BY_GROUPS_NO_GROUP_NAME:
                        subset_group_names.append(group_name)
                    elif group_name != SPLIT_BY_GROUPS_NO_GROUP_NAME:
                        rest_group_names.append(group_name)

                    if is_output_exclusion_rules:
                        self.split_by_groups_exclusion_output_handler(group_name, subset, rests)
                    else:
                        self.split_by_groups_output_handler(group_name, subset, rests)

                    self._write_split_by_groups_group_names(subset_group_names, rest_group_names)

            except Exception as e:
                if os.getenv(REPORT_ERROR_KEY):
                    raise e
                else:
                    click.echo(e, err=True)
                    click.echo(click.style(
                        "Error: the service failed to split subset.", fg='red'),
                        err=True)
                    exit(1)

        def run(self):
            if (not self._is_split_by_groups() and bin_target is None) or (self._is_split_by_groups() and bin_target):
                raise click.BadOptionUsage(
                    "--bin or --split-by-groups/--split-by-groups-with-rest",
                    "Missing option '--bin' or '--split-by-groups/--split-by-groups-with-rest'")

            if self._is_split_by_groups():
                self.split_by_group_names()
            else:
                self.split_by_bin()

    context.obj = SplitSubset(dry_run=context.obj.dry_run)
