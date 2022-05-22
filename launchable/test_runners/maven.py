import os
import click
from . import launchable


@click.option('--from-file', 'from_files', required=False, multiple=True, type=click.Path(exists=True))
@click.argument('source_roots', required=False, nargs=-1)
@launchable.subset
def subset(client, source_roots, from_files):
    def file2test(f: str):
        if f.endswith('.java') or f.endswith(".scala") or f.endswith(".kt"):
            f = f[:f.rindex('.')]   # remove extension
            # directory -> package name conversion
            cls_name = f.replace(os.path.sep, '.')
            return [{"type": "class", "name": cls_name}]
        else:
            return None

    if len(from_files) > 0:
        for file in from_files:
            with open(file, 'r') as f:
                lines = f.readlines()
                for l in lines:
                    client.test_paths.append(
                        [{"type": "class", "name": l.strip()}])
    else:

        for root in source_roots:
            client.scan(root, '**/*', file2test)

    client.run()


split_subset = launchable.CommonSplitSubsetImpls(__name__).split_subset()
record_tests = launchable.CommonRecordTestImpls(__name__).report_files()
