import re

from ..testpath import TestPath
from . import smart_tests


def make_test_path(cls, case) -> TestPath:
    return [{'type': 'class', 'name': cls}, {'type': 'testcase', 'name': case}]


@smart_tests.subset
def subset(client):
    cls = ''
    class_pattern = re.compile(r'^([^\.]+)\.')
    case_pattern = re.compile(r'^  ([^ ]+)')
    for label in map(str.rstrip, client.stdin()):
        # handle Google Test's --gtest_list_tests output
        # FooTest.
        #  Bar
        #  Baz
        gtest_class = class_pattern.match(label)
        if gtest_class:
            cls = gtest_class.group(1)
        gtest_case = case_pattern.match(label)
        if gtest_case and cls:
            case = gtest_case.group(1)
            client.test_path(make_test_path(cls, case))

    client.formatter = lambda x: x[0]['name'] + "." + x[1]['name']
    client.run()


split_subset = smart_tests.CommonSplitSubsetImpls(__name__,
                                                  formatter=lambda x: x[0]['name'] + "." + x[1]['name']).split_subset()

record_tests = smart_tests.CommonRecordTestImpls(__name__).report_files()
