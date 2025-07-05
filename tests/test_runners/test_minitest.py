import gzip
import json
import os
from pathlib import Path
from unittest import mock

import responses  # type: ignore

from smart_tests.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase
from tests.helper import ignore_warnings


class MinitestTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_test_minitest(self):
        result = self.cli('record', 'test', 'minitest', '--session', self.session_name,
                          '--build', self.build_name, str(self.test_files_dir) + "/")
        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_test_minitest_chunked(self):
        result = self.cli('record', 'test', 'minitest', '--session', self.session_name, '--build', self.build_name,
                          '--post-chunk', 5, str(self.test_files_dir) + "/")
        self.assert_success(result)

        payload1 = json.loads(gzip.decompress(self.find_request('/events').request.body).decode())
        expected1 = self.load_json_from_file(self.test_files_dir.joinpath('record_test_result_chunk1.json'))

        payload2 = json.loads(gzip.decompress(self.find_request('/events', 1).request.body).decode())
        expected2 = self.load_json_from_file(self.test_files_dir.joinpath('record_test_result_chunk2.json'))

        # concat 1st and 2nd request for unstable order
        self.assert_json_orderless_equal(expected1['events'] + expected2['events'],
                                         payload1['events'] + payload2['events'])

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    @ignore_warnings
    def test_subset(self):
        test_path = Path("test", "example_test.rb")
        responses.replace(responses.POST,
                          f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/{self.workspace}/subset",
                          json={'testPaths': [[{'name': str(test_path)}]],
                                'rest': [],
                                'subsettingId': 123,
                                'summary': {
                                    'subset': {
                                        'duration': 10,
                                        'candidates': 1,
                                        'rate': 100},
                                    'rest': {
                                        'duration': 0,
                                        'candidates': 0,
                                        'rate': 0}},
                                "isBrainless": False,
                                },
                          status=200)

        result = self.cli('subset', 'minitest', '--session', self.session_name, '--build', self.build_name,
                          '--target', '20%', '--base', str(self.test_files_dir), str(self.test_files_dir) + "/test/**/*.rb")

        self.assert_success(result)

        output = Path(self.test_files_dir, "test", "example_test.rb")
        self.assertIn(str(output), result.output)

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_subset_with_invalid_path(self):
        result = self.cli('subset', 'minitest', '--session', self.session_name, '--build', self.build_name,
                          '--target', '20%', '--base', str(self.test_files_dir), str(self.test_files_dir) + "/dummy")

        self.assert_success(result)

        self.assertTrue("Error: no tests found matching the path." in result.output)

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    @ignore_warnings
    def test_subset_split(self):
        test_path = Path("test", "example_test.rb")
        responses.replace(responses.POST,
                          f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/{self.workspace}/subset",
                          json={'testPaths': [[{'name': str(test_path)}]],
                                'rest': [],
                                'subsettingId': 123,
                                'summary': {'subset': {'duration': 10,
                                                       'candidates': 1,
                                                       'rate': 100},
                                            'rest': {'duration': 0,
                                                     'candidates': 0,
                                                     'rate': 0}},
                                "isBrainless": False,
                                },
                          status=200)

        result = self.cli('subset',
                          'minitest',
                          '--session',
                          self.session_name,
                          '--build',
                          self.build_name,
                          '--target',
                          '20%',
                          '--base',
                          str(self.test_files_dir),
                          '--split',
                          str(self.test_files_dir) + "/test/**/*.rb")

        self.assert_success(result)

        self.assertIn('subset/123', result.output)
