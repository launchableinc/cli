import os
from typing import List
import click
from . import launchable


@click.option('--from-file', 'from_files', required=False, multiple=True, type=click.Path(exists=True))
@click.argument('source_roots', required=False, nargs=-1)
@launchable.subset
def subset(client, source_roots, from_files):

    def is_file(f: str) -> bool:
        return (f.endswith('.java') or f.endswith(".scala") or f.endswith(".kt"))

    def file2class_test_path(f: str) -> List:
        f = f[:f.rindex('.')]   # remove extension
        # directory -> package name conversion
        cls_name = f.replace(os.path.sep, '.')
        return [{"type": "class", "name": cls_name}]

    def file2test(f: str):
        if is_file(f):
            return file2class_test_path(f)
        else:
            return None

    if len(from_files) > 0:
        for file in from_files:
            with open(file, 'r') as f:
                lines = f.readlines()
                for l in lines:
                    # trim trailing newline
                    l = l.strip()

                    if is_file(l):
                        client.test_paths.append(file2class_test_path(l))
                    else:
                        client.test_paths.append(
                            [{"type": "class", "name": l}])
    else:

        for root in source_roots:
            client.scan(root, '**/*', file2test)

    client.run()


split_subset = launchable.CommonSplitSubsetImpls(__name__).split_subset()
record_tests = launchable.CommonRecordTestImpls(__name__).report_files()
