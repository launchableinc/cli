import click
import urllib.parse

from . import launchable
from ..testpath import TestPath, parse_test_path, unparse_test_path


@click.argument('test_path_file', required=True, type=click.File('r'))
@launchable.subset
def subset(client, test_path_file):
    """Subset tests

    TEST_PATH_FILE is a file that contains test paths (e.g.
    "file=a.py#class=classA") one per line. Lines start with a hash ('#') are
    considered as a comment and ignored.
    """
    tps = [s.strip() for s in test_path_file.readlines()]
    for tp_str in tps:
        if not tp_str or tp_str.startswith('#'):
            continue
        try:
            tp = parse_test_path(tp_str)
        except ValueError as e:
            exit(e.args[0])
        client.test_path(tp)

    client.formatter = unparse_test_path
    client.separator = '\n'
    client.run()


split_subset = launchable.CommonSplitSubsetImpls(
    __name__, formatter=unparse_test_path, seperator='\n').split_subset()
