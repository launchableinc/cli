import re

from . import launchable
from ..testpath import TestPath


def make_test_path(cls, case) -> TestPath:
    return [{'type': 'class', 'name': cls}, {'type': 'testcase', 'name': case}]


@launchable.subset
def subset(client):
    cls = ''
    for label in map(str.rstrip, client.stdin()):
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

    client.formatter = lambda x: x[0]['name'] + "." + x[1]['name']
    client.run()


split_subset = launchable.CommonSplitSubsetImpls(
    __name__, formatter=lambda x: x[0]['name'] + "." + x[1]['name']).split_subset()

record_tests = launchable.CommonRecordTestImpls(__name__).report_files()
