import sys
import re
import click

from . import launchable
from ..testpath import TestPath


def make_test_path(cls, case) -> TestPath:
    return [{'type': 'class', 'name': cls}, {'type': 'testcase', 'name': case}]


@launchable.subset
def subset(client):
    cls = ''
    for label in map(str.rstrip, sys.stdin):
        # handle Google Test's --gtest_list_tests output
        # FooTest.
        #  Bar
        #  Baz
        gtest_class = re.match(r'^([^\.]+)\.', label)
        if gtest_class:
            cls = gtest_class.group(1)
        gtest_case = re.match(r'^  ([^ ]+)', label)
        if gtest_case and cls:
            case = gtest_case.group(1)
            client.test_path(make_test_path(cls, case))
        
        # handle ctest -N output
        # Test #1: FooTest.Bar -> (FooTest, Bar)
        ctest_result = re.match(r'^  Test #\d+: ([^ ]+)$', label)
        if ctest_result:
            (cls, case) = ctest_result.group(1).split('.')
            client.test_path(make_test_path(cls, case))

    client.formatter = lambda x: x[0]['name'] + "." + x[1]['name']
    client.run()


record_tests = launchable.CommonRecordTestImpls(__name__).report_files()
