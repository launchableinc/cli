from typing import Dict, List, Optional
import click
from . import launchable
import os


@click.option('--test-compile-created-file', 'test_compile_created_file', required=False, multiple=True, type=click.Path(exists=True), help="Please run `mvn test-compile` command to create input file for this option")
@click.argument('source_roots', required=False, nargs=-1)
@launchable.subset
def subset(client, source_roots, test_compile_created_file):

    def is_file(f: str) -> bool:
        return (f.endswith('.java') or f.endswith(".scala") or f.endswith(".kt") or f.endswith(".class"))

    def file2class_test_path(f: str) -> List[Dict[str, str]]:
        # remove extension
        f, _ = os.path.splitext(f)

        # directory -> package name conversion
        cls_name = f.replace(os.path.sep, '.')
        return [{"type": "class", "name": cls_name}]

    def file2test(f: str) -> Optional[List]:
        if is_file(f):
            return file2class_test_path(f)
        else:
            return None

    if len(test_compile_created_file) > 0:
        for file in test_compile_created_file:
            with open(file, 'r') as f:
                lines = f.readlines()
                for l in lines:
                    # trim trailing newline
                    l = l.strip()

                    # ignore inner class
                    # e.g) com/example/Hoge$Inner.class
                    if "$" in l:
                        continue

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
