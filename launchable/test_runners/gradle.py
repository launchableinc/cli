import os

import click

from . import launchable
from ..engine import Optimize
from ..utils.file_name_pattern import jvm_test_pattern

@launchable.optimize
class GradleOptimize(Optimize):
    @click.argument('source_roots', required=True, nargs=-1)
    def enumerate_tests(self, source_roots):
        def file2test(f: str):
            if jvm_test_pattern.match(f):
                f = f[:f.rindex('.')]   # remove extension
                # directory -> package name conversion
                cls_name = f.replace(os.path.sep, '.')
                return [{"type": "class", "name": cls_name}]
            else:
                return None

        for root in source_roots:
            self.scan(root, '**/*', file2test)

    # if we allow the optimize function to take click decoration
    # it becomes impossible to lift click annotations from enumerate_tests into the appropriate commands
    @click.option('--bare',
                  help='outputs class names alone',
                  default=False,
                  is_flag=True
    )
    def init(self, bare):
        if bare:
            self.formatter = lambda x: x[0]['name']
        else:
            self.formatter = lambda x: "--tests {}".format(x[0]['name'])
            self.separator = ' '


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
