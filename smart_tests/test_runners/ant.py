import os
from typing import Annotated, List

import typer

from ..utils.file_name_pattern import jvm_test_pattern
from . import smart_tests


@smart_tests.subset
def subset(
    client,
    source_roots: Annotated[List[str], typer.Argument(
        help="Source directories to scan for test files"
    )]
):
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


split_subset = smart_tests.CommonSplitSubsetImpls(__name__).split_subset()
record_tests = smart_tests.CommonRecordTestImpls(__name__).report_files()
