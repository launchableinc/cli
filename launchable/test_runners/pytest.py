from typing import List
from os.path import *
import click
import os
import glob
from . import launchable
from ..utils.file_name_pattern import pytest_test_pattern

# Please specify junit_family=legacy for pytest report format. if using pytest version 6 or higher.
# - pytest has changed its default test report format from xunit1 to xunit2 since version 6.
#   - https://docs.pytest.org/en/latest/deprecations.html#junit-family-default-value-change-to-xunit2
# - The xunit2 format no longer includes file names.
#   - It is possible to output in xunit1 format by specifying junit_family=legacy.
#   - The xunit1 format includes the file name.
@click.argument('source_roots', required=True, nargs=-1)
@launchable.subset
def subset(client, source_roots: List[str]):
    def add(f: str):
        if pytest_test_pattern.match(basename(f)):
            client.test_path([{"type": "file", "name": os.path.normpath(f)}])
    for root in source_roots:
        for b in glob.iglob(root):
            if isdir(b):
                for t in glob.iglob(join(b, '**/*.py'), recursive=True):
                    add(t)
            else:
                add(b)
    client.run()


split_subset = launchable.CommonSplitSubsetImpls(__name__).split_subset()

record_tests = launchable.CommonRecordTestImpls(__name__).report_files()
