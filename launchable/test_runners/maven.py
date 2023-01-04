import os
from typing import Dict, List, Optional

import click

from launchable.utils import glob

from . import launchable

# Surefire has the default inclusion pattern
# https://maven.apache.org/surefire/maven-surefire-plugin/test-mojo.html#includes
# and the default exclusion pattern
# https://maven.apache.org/surefire/maven-surefire-plugin/test-mojo.html#excludes
# these variables emulates those effects.
# TODO: inclusion/exclusion are user configurable patterns, so it should be user configurable
# beyond that and to fully generalize this, there's internal discussion of
# this at https://launchableinc.atlassian.net/l/c/TXDJnn09
includes = [glob.compile(x) for x in [
    # HACK: we check extensions outside the glob. We seem to allow both source
    # file enumeration and class file enumeration
    '**/Test*.*',
    '**/*Test.*',
    '**/*Tests.*',
    '**/*TestCase.*'
]]
excludes = [glob.compile(x) for x in [
    '**/*$*'
]]

# Test if a given path name is a test that Surefire recognizes


def is_file(f: str) -> bool:
    if not (f.endswith('.java') or f.endswith(".scala") or f.endswith(".kt") or f.endswith(".class")):
        return False
    for p in excludes:
        if p.fullmatch(f):
            return False
    for p in includes:
        if p.fullmatch(f):
            return True
    return False


@click.option(
    '--test-compile-created-file',
    'test_compile_created_file',
    required=False,
    multiple=True,
    type=click.Path(exists=True),
    help="Please run `mvn test-compile` command to create input file for this option",
)
@click.argument('source_roots', required=False, nargs=-1)
@launchable.subset
def subset(client, source_roots, test_compile_created_file):

    def file2class_test_path(f: str) -> List[Dict[str, str]]:
        # remove extension
        f, _ = os.path.splitext(f)

        # directory -> package name conversion
        cls_name = f.replace(os.path.sep, '.')
        return [{"type": "class", "name": cls_name}]

    def file2test(f: str) -> Optional[List]:
        if is_file(f):
            return file2class_test_path(f)
        else:
            return None

    if len(test_compile_created_file) > 0:
        if len(source_roots) != 0:
            click.echo(click.style(
                "Warning: SOURCE_ROOTS are ignored when --test-compile-created-file is used", fg="yellow"),
                err=True)

        for file in test_compile_created_file:
            with open(file, 'r') as f:
                lines = f.readlines()
                if len(lines) == 0:
                    click.echo(click.style(
                        "Warning: --test-compile-created-file {} is empty".format(file), fg="yellow"),
                        err=True)

                for l in lines:
                    # trim trailing newline
                    l = l.strip()

                    path = file2test(l)
                    if path:
                        client.test_paths.append(path)
    else:
        for root in source_roots:
            client.scan(root, '**/*', file2test)

    client.run()


@launchable.split_subset
def split_subset(client):
    def format_same_bin(s: str) -> List[Dict[str, str]]:
        return [{"type": "class", "name": s}]

    client.same_bin_formatter = format_same_bin
    client.run()


# TestNG produces surefire-reports/testng-results.xml in TestNG's native format.
# Surefire produces TEST-*.xml in JUnit format (see Surefire's StatelessXmlReporter.getReportFile)
# In addition, TestNG also produces surefire-reports/junitreports/TEST-*.xml
# (see TestNG's JUnitReportReporter.getFileName)
# And there are more test reports in play.
#
# So to collectly find tests without duplications, we need to find surefire-reports/TEST-*.xml
# not surefire-reports/**/TEST-*.xml nor surefire-reports/*.xml
record_tests = launchable.CommonRecordTestImpls(__name__).report_files(file_mask="TEST-*.xml")
