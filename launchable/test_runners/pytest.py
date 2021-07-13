from typing import List
from os.path import *
import click
import os
import glob
from . import launchable
from ..utils.file_name_pattern import pytest_test_pattern


@click.argument('source_roots', required=True, nargs=-1)
@launchable.subset
def subset(client, source_roots: List[str]):
    def add(f: str):
        if pytest_test_pattern.match(basename(f)):
            f = splitext(f)[0]   # remove extension
            # directory -> package name conversion
            cls_name = f.replace(os.path.sep, '.')
            client.test_path([{"type": "class", "name": cls_name}])

    for root in source_roots:
        for b in glob.iglob(root):
            if isdir(b):
                for t in glob.iglob(join(b, '**/*.py'), recursive=True):
                    add(t)
            else:
                add(b)

    client.formatter = lambda x: x[0]['name'].replace('.', os.path.sep) + ".py"
    client.run()


split_subset = launchable.CommonSplitSubsetImpls(
    __name__, formatter=lambda x: x[0]['name'].replace('.', os.path.sep) + ".py").split_subset()

record_tests = launchable.CommonRecordTestImpls(__name__).report_files()
