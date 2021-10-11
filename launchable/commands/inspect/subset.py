from http import HTTPStatus
from tabulate import tabulate
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.http_client import LaunchableClient
import os
import click
from typing import Dict, List


@click.command()
@click.option(
    '--subset-id',
    'subset_id',
    help='subest id',
    required=True,
)
def subset(subset_id):
    subset = []
    rest = []
    try:
        client = LaunchableClient()
        res = client.request("get", "subset/{}".format(subset_id))

        if res.status_code == HTTPStatus.NOT_FOUND:
            click.echo(click.style(
                "Subset {} not found. Check subset ID and try again.".format(subset_id), 'yellow'), err=True)
            exit(1)

        res.raise_for_status()
        subset = res.json()["testPaths"]
        rest = res.json()["rest"]
    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            click.echo(e, err=True)
        click.echo(click.style(
            "Warning: failed to inspect subset", fg='yellow'),
            err=True)

    header = ["Order", "Test Path", "In Subset", "Estimated duration (sec)"]

    subset_row = convert_row(subset, 1, True)
    rest_row = convert_row(rest, len(subset) + 1, False)
    rows = subset_row + rest_row

    click.echo(tabulate(rows, header, tablefmt="github"))


def convert_row(list: List[Dict], order: int, is_subset: bool):
    """
    list: testPaths or rest in response to a get subset API
    order: start number of order
    is_subset: in subset or not
    """
    return [[order + i, "#".join([path["type"] + "=" + path["name"]
                                  for path in l["testPath"]]), "✔"
             if is_subset else "", "{:0.4f}".format(l["duration"] / 1000)]
            for i, l in enumerate(list)]
