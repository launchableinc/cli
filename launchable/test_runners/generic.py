#
# The most bare-bone versions of the test runner support
#
import click
from . import launchable


@click.argument('tests', required=True, nargs=-1)
@launchable.test_scanner
def scan_tests(optimize, tests):
    for t in tests:
        optimize.test(t)
    optimize.run()


@click.argument('source_roots', required=True, nargs=-1)
@launchable.report_scanner
def scan_reports(scanner, source_roots):
    for root in source_roots:
        scanner.scan(root, '*.xml')
