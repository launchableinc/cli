import os
from typing import List

from ..utils.file_name_pattern import jvm_test_pattern
from . import launchable


# This decorator is converted to Typer annotations in the function signature
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
