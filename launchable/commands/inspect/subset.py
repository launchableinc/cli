import json
import sys
from abc import ABCMeta, abstractmethod
from http import HTTPStatus
from typing import List

import click
from tabulate import tabulate

from ...utils.launchable_client import LaunchableClient


class SubsetResult (object):
    def __init__(self, result: dict, is_subset: bool):
        self._estimated_duration_sec = result.get("duration", 0.0) / 1000  # convert to sec from msec
        self._test_path = "#".join([path["type"] + "=" + path["name"]
                                   for path in result["testPath"] if path.keys() >= {"type", "name"}])
        self._is_subset = is_subset


class SubsetResults(object):
    def __init__(self, results: List[SubsetResult]):
        self._results = results

    def add_subset(self, subset: List):
        for result in subset:
            self._results.append(SubsetResult(result, True))

    def add_rest(self, rest: List):
        for result in rest:
            self._results.append(SubsetResult(result, False))

    def list(self) -> List[SubsetResult]:
        return self.list_subset() + self.list_rest()

    def list_subset(self) -> List[SubsetResult]:
        return [result for result in self._results if result._is_subset]

    def list_rest(self) -> List[SubsetResult]:
        return [result for result in self._results if not result._is_subset]


class SubsetResultAbstractDisplay(metaclass=ABCMeta):
    def __init__(self, results: SubsetResults):
        self._results = results

    @abstractmethod
    def display(self):
        raise NotImplementedError("display method is not implemented")


class SubsetResultTableDisplay(SubsetResultAbstractDisplay):
    def __init__(self, results: SubsetResults):
        super().__init__(results)

    def display(self):
        header = ["Order", "Test Path", "In Subset", "Estimated duration (sec)"]
        rows = []
        for idx, result in enumerate(self._results.list()):
            rows.append(
                [
                    idx + 1,
                    result._test_path,
                    "✔" if result._is_subset else "",
                    result._estimated_duration_sec,
                ]
            )
        click.echo(tabulate(rows, header, tablefmt="github", floatfmt=".2f"))


class SubsetResultJSONDisplay(SubsetResultAbstractDisplay):
    def __init__(self, results: SubsetResults):
        super().__init__(results)

    def display(self):
        result_json = {
            "subset": [],
            "rest": []
        }
        for result in self._results.list_subset():
            result_json["subset"].append({
                "test_path": result._test_path,
                "estimated_duration_sec": round(result._estimated_duration_sec, 2),
            })
        for result in self._results.list_rest():
            result_json["rest"].append({
                "test_path": result._test_path,
                "estimated_duration_sec": round(result._estimated_duration_sec, 2),
            })

        click.echo(json.dumps(result_json, indent=2))


@click.command()
@click.option(
    '--subset-id',
    'subset_id',
    help='subest id',
    required=True,
)
@click.option(
    '--json',
    'is_json_format',
    help='display JSON format',
    is_flag=True
)
@click.pass_context
def subset(context: click.core.Context, subset_id: int, is_json_format: bool):
    subset = []
    rest = []
    client = LaunchableClient(app=context.obj)
    try:
        res = client.request("get", "subset/{}".format(subset_id))

        if res.status_code == HTTPStatus.NOT_FOUND:
            click.echo(click.style(
                "Subset {} not found. Check subset ID and try again.".format(subset_id), 'yellow'), err=True)
            sys.exit(1)

        res.raise_for_status()
        subset = res.json()["testPaths"]
        rest = res.json()["rest"]
    except Exception as e:
        client.print_exception_and_recover(e, "Warning: failed to inspect subset")

    results = SubsetResults([])
    results.add_subset(subset)
    results.add_rest(rest)

    displayer: SubsetResultAbstractDisplay
    if is_json_format:
        displayer = SubsetResultJSONDisplay(results)
    else:
        displayer = SubsetResultTableDisplay(results)

    displayer.display()
