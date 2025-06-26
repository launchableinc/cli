import os
from typing import Annotated, List, Optional

import typer

from launchable.testpath import TestPath

from ..app import Application
from ..utils.launchable_client import LaunchableClient
from ..utils.typer_types import validate_fraction
from .test_path_writer import TestPathWriter

SPLIT_BY_GROUPS_NO_GROUP_NAME = "nogroup"
SPLIT_BY_GROUP_SUBSET_GROUPS_FILE_NAME = "subset-groups.txt"
SPLIT_BY_GROUP_REST_GROUPS_FILE_NAME = "rest-groups.txt"


app = typer.Typer(name="split-subset", help="Split subsetting tests")


@app.callback()
def split_subset(
    ctx: typer.Context,
    subset_id: Annotated[str, typer.Option(
        "--subset-id",
        help="subset id"
    )],
    bin_target: Annotated[Optional[str], typer.Option(
        "--bin",
        help="bin"
    )] = None,
    rest: Annotated[Optional[str], typer.Option(
        help="output the rest of subset"
    )] = None,
    base: Annotated[Optional[str], typer.Option(
        help="(Advanced) base directory to make test names portable",
        metavar="DIR"
    )] = None,
    same_bin: Annotated[List[str], typer.Option(
        "--same-bin",
        help="(Advanced) gather specified tests into same bin"
    )] = [],
    split_by_groups: Annotated[bool, typer.Option(
        "--split-by-groups",
        help="split by groups that were set by `launchable record tests --group`"
    )] = False,
    split_by_groups_with_rest: Annotated[bool, typer.Option(
        "--split-by-groups-with-rest",
        help="split by groups that were set by `launchable record tests --group` and produces with rest files"
    )] = False,
    split_by_groups_output_dir: Annotated[str, typer.Option(
        help="split results output dir"
    )] = os.getcwd(),
    output_exclusion_rules: Annotated[bool, typer.Option(
        "--output-exclusion-rules",
        help="outputs the exclude test list. Switch the subset and rest."
    )] = False,
):
    app = ctx.obj

    # Parse parameters
    parsed_bin_target = validate_fraction(bin_target) if bin_target else None
    base_path = base
    # same_bin_files = same_bin  # Unused variable
    is_split_by_groups = split_by_groups
    is_split_by_groups_with_rest = split_by_groups_with_rest
    is_output_exclusion_rules = output_exclusion_rules

    if len(subset_id.split("/")) != 2:
        typer.echo(
            typer.style('Error: subset ID cannot be empty. It should be passed with `subset/<subset id>` format.',
                        fg=typer.colors.YELLOW),
            err=True,
        )
        return

    TestPathWriter.base_path = base_path

    # Don't create client here - it will be created by subcommands
    # with the correct test_runner name

    class SplitSubset(TestPathWriter):
        def __init__(self, app: Application):
            super(SplitSubset, self).__init__(app=app)
            # Store all parameters as instance variables
            self.subset_id = subset_id
            self.parsed_bin_target = parsed_bin_target
            self.rest = rest
            self.base_path = base_path
            self.same_bin_files = same_bin
            self.is_split_by_groups = is_split_by_groups
            self.is_split_by_groups_with_rest = is_split_by_groups_with_rest
            self.split_by_groups_output_dir = split_by_groups_output_dir
            self.is_output_exclusion_rules = is_output_exclusion_rules
            # client will be passed to methods when needed

            self.output_handler = self._default_output_handler
            self.exclusion_output_handler = self._default_exclusion_output_handler
            self.split_by_groups_output_handler = self._default_split_by_groups_output_handler
            self.split_by_groups_exclusion_output_handler = self._default_split_by_groups_exclusion_output_handler

        def _default_output_handler(self, output: List[TestPath], rests: List[TestPath]):
            if self.rest:
                self.write_file(self.rest, rests)

            if output:
                self.print(output)

        def _default_exclusion_output_handler(self, subset: List[TestPath], rest: List[TestPath]):
            self.output_handler(rest, subset)

        def _default_split_by_groups_output_handler(self, group_name: str, subset: List[TestPath], rests: List[TestPath]):
            if self.is_split_by_groups_with_rest:
                self.write_file("{}/rest-{}.txt".format(self.split_by_groups_output_dir, group_name), rests)

            if len(subset) > 0:
                self.write_file("{}/subset-{}.txt".format(self.split_by_groups_output_dir, group_name), subset)

        def _default_split_by_groups_exclusion_output_handler(
                self, group_name: str, subset: List[TestPath],
                rests: List[TestPath]):
            self.split_by_groups_output_handler(group_name, rests, subset)

        def _is_split_by_groups(self) -> bool:
            return self.is_split_by_groups or self.is_split_by_groups_with_rest

        def split_by_bin(self, client):
            index, count = 0, 0
            if not self.is_split_by_groups:
                index = self.parsed_bin_target[0]
                count = self.parsed_bin_target[1]

                if (index == 0 or count == 0):
                    typer.echo(
                        typer.style(
                            'Error: invalid bin value. Make sure to set over 0 like `--bin 1/2` but set `--bin {}`'.format(
                                self.parsed_bin_target),
                            fg=typer.colors.YELLOW),
                        err=True,
                    )
                    return

                if count < index:
                    typer.echo(
                        typer.style(
                            'Error: invalid bin value. Make sure to set below 1 like `--bin 1/2`, `--bin 2/2` '
                            'but set `--bin {}`'.format(self.parsed_bin_target),
                            fg=typer.colors.YELLOW),
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
                    "splitByGroups": self.is_split_by_groups
                }

                tests_in_files = []

                if self.same_bin_files is not None and len(self.same_bin_files) > 0:
                    if self.same_bin_formatter is None:
                        raise ValueError("--same-bin option is supported only for gradle test and go-test. "
                                         "Please remove --same-bin option for the other test runner.")
                    same_bins = []
                    for same_bin_file in self.same_bin_files:
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

                res = client.request("POST", "{}/slice".format(self.subset_id), payload=payload)
                res.raise_for_status()

                output_subset = res.json().get("testPaths", [])
                output_rests = res.json().get("rest", [])
                is_observation = res.json().get("isObservation", False)

                if len(output_subset) == 0:
                    typer.echo(typer.style(
                        "Error: no tests found for this subset id.", fg=typer.colors.YELLOW), err=True)
                    return

                if is_observation:
                    output_subset = output_subset + output_rests
                    output_rests = []

                if self.is_output_exclusion_rules:
                    self.exclusion_output_handler(output_subset, output_rests)
                else:
                    self.output_handler(output_subset, output_rests)

            except Exception as e:
                client.print_exception_and_recover(
                    e, "Warning: the service failed to split subset. Falling back to running all tests")
                return

        def _write_split_by_groups_group_names(self, subset_group_names: List[str], rest_group_names: List[str]):
            if self.is_output_exclusion_rules:
                subset_group_names, rest_group_names = rest_group_names, subset_group_names

            if len(subset_group_names) > 0:
                with open("{}/{}".format(self.split_by_groups_output_dir, SPLIT_BY_GROUP_SUBSET_GROUPS_FILE_NAME),
                          "w+", encoding="utf-8") as f:
                    f.write("\n".join(subset_group_names))

            if self.is_split_by_groups_with_rest:
                with open("{}/{}".format(self.split_by_groups_output_dir, SPLIT_BY_GROUP_REST_GROUPS_FILE_NAME),
                          "w+", encoding="utf-8") as f:
                    f.write("\n".join(rest_group_names))

        def split_by_group_names(self, client):
            try:
                res = client.request("POST", "{}/split-by-groups".format(self.subset_id))
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

                    if self.is_output_exclusion_rules:
                        self.split_by_groups_exclusion_output_handler(group_name, subset, rests)
                    else:
                        self.split_by_groups_output_handler(group_name, subset, rests)

                    self._write_split_by_groups_group_names(subset_group_names, rest_group_names)

            except Exception as e:
                client.print_exception_and_recover(e, "Error: the service failed to split subset.", 'red')
                exit(1)

        def run(self, test_runner_name=None):
            if (not self._is_split_by_groups() and self.parsed_bin_target is None) or (
                    self._is_split_by_groups() and self.parsed_bin_target):
                raise typer.BadParameter(
                    "Missing option '--bin' or '--split-by-groups/--split-by-groups-with-rest'")

            # Create client with the correct test runner name
            client = LaunchableClient(test_runner=test_runner_name or "split-subset", app=self.app)

            if self._is_split_by_groups():
                self.split_by_group_names(client)
            else:
                self.split_by_bin(client)

    # Create and store the SplitSubset instance for subcommands to use
    ctx.obj = SplitSubset(app=app)
