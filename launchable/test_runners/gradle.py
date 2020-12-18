import click, os
from . import launchable

@click.argument('source_roots', required=True, nargs=-1)
@launchable.test_scanner
def scan_tests(optimize, source_roots):
    def file2test(f:str):
        if f.endswith('.java') or f.endswith('.scala') or f.endswith('.kt'):
            f = f[:f.rindex('.')]   # remove extension
            f = f.replace(os.path.sep,'.')  # directory -> package name conversion
            return f
        else:
            return None

    for root in source_roots:
        optimize.scan(root, '**/*', file2test)

    optimize.run()



@click.argument('source_roots', required=True, nargs=-1)
@launchable.report_scanner
def scan_reports(scanner, source_roots):
    for root in source_roots:
        scanner.scan(root,"*.xml")
