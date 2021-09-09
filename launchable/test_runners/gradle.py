import os

import click

from . import launchable
from ..utils.file_name_pattern import jvm_test_pattern


@click.option('--bare',
              help='outputs class names alone',
              default=False,
              is_flag=True
              )
@click.argument('source_roots', required=True, nargs=-1)
@launchable.subset
def subset(client, bare, source_roots):
    def file2test(f: str):
        if jvm_test_pattern.match(f):
            f = f[:f.rindex('.')]   # remove extension
            # directory -> package name conversion
            cls_name = f.replace(os.path.sep, '.')
            return [{"type": "class", "name": cls_name}]
        else:
            return None

    for root in source_roots:
        client.scan(root, '**/*', file2test)

    if bare:
        client.formatter = lambda x: x[0]['name']
    else:
        client.formatter = lambda x: "--tests {}".format(x[0]['name'])
        client.separator = ' '

    client.run()


@click.option('--bare',
              help='outputs class names alone',
              default=False,
              is_flag=True
              )
@launchable.split_subset
def split_subset(client, bare):
    if bare:
        client.formatter = lambda x: x[0]['name']
    else:
        client.formatter = lambda x: "--tests {}".format(x[0]['name'])
        client.separator = ' '

    client.run()


record_tests = launchable.CommonRecordTestImpls(__name__).report_files()
