import sys
import re
import click

from . import launchable
from ..testpath import TestPath


@launchable.subset
def subset(client):
    for label in map(str.rstrip, sys.stdin):
        # handle ctest -N output
        # Test #1: FooTest
        ctest_result = re.match(r'^  Test +#\d+: ([^ ]+)$', label)
        if ctest_result:
            case = ctest_result.group(1)
            client.test_path([{'type': 'testcase', 'name': case}])
    client.seperator = '|'
    client.run()


record_tests = launchable.CommonRecordTestImpls(__name__).report_files()
