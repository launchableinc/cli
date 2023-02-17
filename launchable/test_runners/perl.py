import click
from tap.parser import Parser

from . import launchable

subset = launchable.CommonSubsetImpls(__name__).scan_files('*_spec.rb')
split_subset = launchable.CommonSplitSubsetImpls(__name__).split_subset()


@click.argument('reports', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, reports):

    tap_parser = Parser()

    for r in reports:
        for line in tap_parser.parse_file(r):
            print(line)
