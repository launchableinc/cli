import os
import json
import click
from . import launchable


@launchable.subset
def subset(client):
    if client.base_path is None:
        raise click.BadParameter("Please specify base path")

    for line in client.stdin():
        if len(line.strip()) and not line.startswith(">"):
            client.test_path(line.rstrip("\n"))

    client.run()


record_tests = launchable.CommonRecordTestImpls(__name__).report_files()
