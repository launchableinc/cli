import click
from junitparser import TestCase, TestSuite  # type: ignore

from ..testpath import TestPath
from . import launchable

subset = launchable.CommonSubsetImpls(__name__).scan_files('*_test.rb')
split_subset = launchable.CommonSplitSubsetImpls(__name__).split_subset()

TEST_PATH_ORDER = {"file": 1, "class": 2, "testcase": 3}


@click.argument('reports', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, reports):
    default_path_builder = client.path_builder

    def path_builder(case: TestCase, suite: TestSuite, report_file: str) -> TestPath:
        test_path = default_path_builder(case, suite, report_file)
        if not any(item.get("type") == "class" for item in test_path):
            # mintiest-ci sets a class name in name attribute in testsuite tag.
            # https://github.com/CircleCI-Public/minitest-ci/blob/v3.4.0/lib/minitest/ci_plugin.rb#L86-L87
            # https://github.com/CircleCI-Public/minitest-ci/blob/v3.4.0/lib/minitest/ci_plugin.rb#L132
            classname = suite._elem.attrib.get("name")
            if classname:
                test_path.append({"type": "class", "name": classname})
                test_path = sorted(test_path, key=lambda x: TEST_PATH_ORDER[x["type"]])
        return test_path

    client.path_builder = path_builder

    launchable.CommonRecordTestImpls.load_report_files(client=client, source_roots=reports)
