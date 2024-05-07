import gzip
import json
import os
import tempfile
from pathlib import Path
from unittest import mock

import responses  # type: ignore

from launchable.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase
from tests.helper import ignore_warnings


class MinitestTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_minitest(self):
        result = self.cli('record', 'tests', '--session', self.session, 'minitest', str(self.test_files_dir) + "/")
        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')

    # For testing https://github.com/launchableinc/cli/pull/846/files#r1591707246.
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_minitest_test_path_order(self):
        with tempfile.TemporaryDirectory() as tempdir:
            test_path_file = os.path.join(tempdir, 'tests.xml')
            with open(test_path_file, 'w') as f:
                f.write("""<?xml version="1.0" encoding="UTF-8"?>
<testsuite time='1.614255' skipped='0' failures='0' errors='0' name="UserTest" assertions='1' tests='1' timestamp="2020-12-23T13:10:01+09:00">
  <testcase time='1.614255' file="test/models/open_class_user_test.rb" name="test_should_not_save_user_without_name_2" assertions='1'>
  </testcase>
</testsuite>""")  # noqa: E501
            result = self.cli('record', 'tests', '--session', self.session, 'minitest', test_path_file)
            self.assert_success(result)
            payload = json.loads(gzip.decompress(self.find_request('/events').request.body).decode())
            self.assertEqual(
                payload['events'][0]['testPath'],
                [{'type': 'file', 'name': 'test/models/open_class_user_test.rb'},
                 {'type': 'class', 'name': 'UserTest'},
                 {'type': 'testcase', 'name': 'test_should_not_save_user_without_name_2'}])

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_minitest_chunked(self):
        result = self.cli('record', 'tests', '--session', self.session,
                          '--post-chunk', 5, 'minitest', str(self.test_files_dir) + "/")
        self.assert_success(result)

        payload1 = json.loads(gzip.decompress(self.find_request('/events').request.body).decode())
        expected1 = self.load_json_from_file(self.test_files_dir.joinpath('record_test_result_chunk1.json'))

        payload2 = json.loads(gzip.decompress(self.find_request('/events', 1).request.body).decode())
        expected2 = self.load_json_from_file(self.test_files_dir.joinpath('record_test_result_chunk2.json'))

        # concat 1st and 2nd request for unstable order
        self.assert_json_orderless_equal(expected1['events'] + expected2['events'],
                                         payload1['events'] + payload2['events'])

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    @ignore_warnings
    def test_subset(self):
        test_path = Path("test", "example_test.rb")
        responses.replace(responses.POST,
                          "{}/intake/organizations/{}/workspaces/{}/subset".format(get_base_url(),
                                                                                   self.organization,
                                                                                   self.workspace),
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

        result = self.cli('subset', '--target', '20%', '--session', self.session, '--base', str(self.test_files_dir),
                          'minitest', str(self.test_files_dir) + "/test/**/*.rb")

        self.assert_success(result)

        output = Path(self.test_files_dir, "test", "example_test.rb")
        self.assertIn(str(output), result.output)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_with_invalid_path(self):
        result = self.cli('subset', '--target', '20%', '--session', self.session, '--base', str(self.test_files_dir),
                          'minitest', str(self.test_files_dir) + "/dummy")

        self.assert_success(result)

        self.assertTrue("Error: no tests found matching the path." in result.output)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    @ignore_warnings
    def test_subset_split(self):
        test_path = Path("test", "example_test.rb")
        responses.replace(responses.POST,
                          "{}/intake/organizations/{}/workspaces/{}/subset".format(get_base_url(),
                                                                                   self.organization,
                                                                                   self.workspace),
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

        result = self.cli('subset', '--target', '20%', '--session', self.session, '--base',
                          str(self.test_files_dir), '--split', 'minitest', str(self.test_files_dir) + "/test/**/*.rb")

        self.assert_success(result)

        self.assertIn('subset/123', result.output)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    @ignore_warnings
    def test_split_subset(self):
        test_path = Path("test", "example_test.rb")
        responses.replace(responses.POST,
                          "{}/intake/organizations/{}/workspaces/{}/subset/456/slice".format(get_base_url(),
                                                                                             self.organization,
                                                                                             self.workspace),
                          json={'testPaths': [[{'name': str(test_path)}]],
                                'rest': [],
                                'subsettingId': 123},
                          status=200)

        rest = tempfile.NamedTemporaryFile(delete=False)
        result = self.cli('split-subset', '--subset-id', 'subset/456', '--base', str(self.test_files_dir),
                          '--bin', '2/2', '--rest', rest.name, 'minitest')

        self.assert_success(result)

        output = Path(self.test_files_dir, "test", "example_test.rb")
        self.assertEqual(str(output), result.output.rstrip("\n"))
        self.assertEqual(rest.read().decode().rstrip("\n"), "")
        rest.close()
        os.unlink(rest.name)
