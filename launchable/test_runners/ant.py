import os
from typing import List
import click
from . import launchable
from ..utils.file_name_pattern import jvm_test_pattern


@click.argument('source_roots', required=True, nargs=-1)
@launchable.subset
def subset(client, source_roots: List[str]):
    def file2test(f: str):
        if jvm_test_pattern.match(f):
            f = f[:f.rindex('.')]   # remove extension
            # directory -> package name conversion
            cls_name = f.replace(os.path.sep, '.')
            return [{"type": "class", "name": cls_name}]
        else:
            return None

    for root in source_roots:
        client.scan(root.rstrip('/'), "**/*Test.java", file2test)

    client.run()


split_subset = launchable.CommonSplitSubsetImpls(__name__).split_subset()
record_tests = launchable.CommonRecordTestImpls(__name__).report_files()
