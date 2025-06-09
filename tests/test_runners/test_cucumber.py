import glob
import os
from unittest import mock

import responses  # type: ignore

from launchable.test_runners.cucumber import _create_file_candidate_list, clean_uri
from launchable.utils.session import write_build
from tests.cli_test_case import CliTestCase


class CucumberTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test(self):
        reports = []
        for f in glob.iglob(str(self.test_files_dir.joinpath("report/*.xml")), recursive=True):
            reports.append(f)

        # emulate launchable record build
        write_build(self.build_name)

        result = self.cli('record', 'tests', '--base', str(self.test_files_dir), 'cucumber', *reports)

        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_from_json(self):
        reports = []
        for f in glob.iglob(str(self.test_files_dir.joinpath("report/*.json")), recursive=True):
            reports.append(f)

        # emulate launchable record build
        write_build(self.build_name)

        result = self.cli('record', 'tests', 'cucumber', "--json", *reports)

        self.assert_success(result)
        self.assert_record_tests_payload('record_test_json_result.json')

    def test_create_file_candidate_list(self):
        self.assertCountEqual(_create_file_candidate_list("a-b"), ["a/b", "a-b"])
        self.assertCountEqual(_create_file_candidate_list("a-b-c"), ["a/b/c", "a-b/c", "a/b-c", "a-b-c"])
        self.assertCountEqual(_create_file_candidate_list("a_b_c"), ["a_b_c"])

    def test_clean_uri(self):
        self.assertEqual(clean_uri('foo/bar/baz.feature'), 'foo/bar/baz.feature')
        self.assertEqual(clean_uri('file:foo/bar/baz.feature'), 'foo/bar/baz.feature')
        self.assertEqual(clean_uri('classpath:foo/bar/baz.feature'), 'foo/bar/baz.feature')
