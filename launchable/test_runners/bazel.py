import click, sys, os, glob
from . import launchable
from os.path import join

@launchable.test_scanner
def scan_tests(optimize):
    # Read targets from stdin, which generally looks like //foo/bar:zot
    for pkg in sys.stdin:
        # //foo/bar:zot -> foo/bar/zot
        optimize.test(pkg.lstrip('/').replace(':','/'))

    optimize.run()



@click.argument('workspace', required=True)
@launchable.report_scanner
def scan_reports(scanner, workspace):
    """
    Takes Bazel workspace, then report all its test results
    """
    base = join(workspace, 'bazel-testlogs')
    if not os.path.exists(base):
        exit("No such directory: %s" % base)
    for xml in glob.iglob(join(base, '**/test.xml'), recursive=True):
        pkg = xml[len(base)+1:-8]    # extract the part that matches '**' which represents the pacakge
        scanner.scan(xml, pkg)  # TODO: how we do this depends on how we design this abstraction
