import click
import os
import glob
from . import launchable


@click.argument('source_roots', required=True, nargs=-1)
@launchable.subset
def subset(client, source_roots):
    def file2test(f: str):
        if f.endswith('.java') or f.endswith('.scala') or f.endswith('.kt'):
            f = f[:f.rindex('.')]   # remove extension
            # directory -> package name conversion
            cls_name = f.replace(os.path.sep, '.')
            return [{"type": "class", "name": cls_name}]
        else:
            return None

    for root in source_roots:
        client.scan(root, '**/*', file2test)

    client.run()


@click.argument('source_roots', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, source_roots):
    # Accept both file names and GLOB patterns
    # Simple globs like '*.xml' can be dealt with by shell, but
    # not all shells consistently deal with advanced GLOBS like '**'
    # so it's worth supporting it here.
    for root in source_roots:
        match = False
        for t in glob.iglob(root, recursive=True):
            match = True
            if os.path.isdir(t):
                client.scan(t, "*.xml")
            else:
                client.report(t)

        if not match:
            # By following the shell convention, if the file doesn't exist or GLOB doesn't match anything,
            # raise it as an error. Note this can happen for reasons other than a configuration error.
            # For example, if a build catastrophically failed and no tests got run.
            click.echo("No matches found: " % root, err=True)
            # intentionally exiting with zero
            return

    client.run()
