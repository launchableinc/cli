from pathlib import Path
import os
import glob
import responses  # type: ignore
import json
import gzip
from launchable.test_runners.cucumber import _create_file_candidate_list
from unittest import mock
from launchable.utils.session import write_build
from tests.cli_test_case import CliTestCase


class CucumberTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath(
        '../data/cucumber/').resolve()

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test(self):
        reports = []
        for f in glob.iglob(str(self.test_files_dir.joinpath(
                "report/*.xml")), recursive=True):
            reports.append(f)

        # emulate launchable record build
        write_build(self.build_name)

        result = self.cli('record', 'tests', '--base', str(self.test_files_dir),
                          'cucumber', *reports)

        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[2].request.body).decode())
        for c in payload['events']:
            del c['created_at']

        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('record_test_result.json'))
        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_from_json(self):
        reports = []
        for f in glob.iglob(str(self.test_files_dir.joinpath(
                "report/*.json")), recursive=True):
            reports.append(f)

        # emulate launchable record build
        write_build(self.build_name)

        result = self.cli('record', 'tests',
                          'cucumber', "--json", *reports)

        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[2].request.body).decode())

        for c in payload['events']:
            del c['created_at']

        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('record_test_json_result.json'))
        self.assert_json_orderless_equal(expected, payload)

    def test_create_file_candidate_list(self):
        self.assertCountEqual(
            _create_file_candidate_list(
                "a-b"), ["a/b", "a-b"]
        )
        self.assertCountEqual(
            _create_file_candidate_list(
                "a-b-c"), ["a/b/c", "a-b/c", "a/b-c", "a-b-c"]
        )
        self.assertCountEqual(
            _create_file_candidate_list(
                "a_b_c"), ["a_b_c"]
        )
