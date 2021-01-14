import click
import os
import sys
from . import launchable


@click.argument('files', required=True, nargs=-1)
@launchable.subset
def subset(client, files):
    def parse(fname: str):
        '''
        Scan a file, directory full of *.rb, or @FILE
        '''
        if os.path.isdir(fname):
            client.scan(fname, '**/*_test.rb')
        elif fname == '@-':
            # read stdin
            for l in sys.stdin:
                parse(l)
        elif fname.startswith('@'):
            # read response file
            with open(fname[1:]) as f:
                for l in f:
                    parse(l)
        else:
            # assume it's a file
            client.test(fname)

    for f in files:
        parse(f)

    client.run()


record_tests = launchable.CommonRecordTestImpls(__name__).report_files()
