import os
import click
from ...utils.http_client import LaunchableClient
from ...utils.env_keys import REPORT_ERROR_KEY
from tabulate import tabulate


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
        res.raise_for_status()
        subset = res.json()["testPaths"]
        rest = res.json()["rest"]
    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            click.echo(e, err=True)
        click.echo(click.style(
            "Warning: the failed to inspect subset", fg='yellow'),
            err=True)

    header = ["Order", "Test Path", "In Subset", "Estimated duration (min)"]
    rows = []
    order = 1
    for s in subset:
        rows.append([order, "#".join([path["type"] + "=" + path["name"]
                                      for path in s["testPath"]]), "✔", "{:0.4f}".format(s["duration"] / 60 / 1000)])  # msec to min
        order = order + 1

    for s in rest:
        rows.append([order, "#".join([path["type"] + "=" + path["name"]
                                      for path in s["testPath"]]), "", "{:0.4f}".format(s["duration"] / 60 / 1000)])  # msec to min
        order = order + 1

    click.echo(tabulate(rows, header, tablefmt="github"))
