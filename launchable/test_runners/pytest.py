from typing import List
import click
from . import launchable
from ..utils.file_name_pattern import pytest_test_pattern

@click.argument('source_roots', required=True, nargs=-1)
@launchable.subset
def subset(client, source_roots: List[str]):
    for root in source_roots:
        client.scan(root.rstrip('/'), "**/*.py", lambda f: f if pytest_test_pattern.match(f) else False)

    client.run()

record_tests = launchable.CommonRecordTestImpls(__name__).report_files()
