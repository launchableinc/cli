from pathlib import Path
import responses  # type: ignore
import json
import gzip
import os
from pathlib import Path
from unittest import mock
from tests.cli_test_case import CliTestCase
from launchable.utils.http_client import get_base_url
import tempfile
from tests.helper import ignore_warnings


class MinitestTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath(
        '../data/minitest/').resolve()
    result_file_path = test_files_dir.joinpath('record_test_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_minitest(self):
        result = self.cli('record', 'tests',  '--session',
                          self.session, 'minitest', str(self.test_files_dir) + "/")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[1].request.body).decode())

        expected = self.load_json_from_file(self.result_file_path)
        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_minitest_chunked(self):
        result = self.cli('record', 'tests',  '--session', self.session,
                          '--post-chunk', 5, 'minitest', str(self.test_files_dir) + "/")
        self.assertEqual(result.exit_code, 0)

        payload1 = json.loads(gzip.decompress(
            responses.calls[1].request.body).decode())
        expected1 = self.load_json_from_file(
            self.test_files_dir.joinpath('record_test_result_chunk1.json'))

        payload2 = json.loads(gzip.decompress(
            responses.calls[2].request.body).decode())
        expected2 = self.load_json_from_file(
            self.test_files_dir.joinpath('record_test_result_chunk2.json'))

        # concat 1st and 2nd request for unstable order
        self.assert_json_orderless_equal(
            expected1['events'] + expected2['events'], payload1['events'] + payload2['events'])

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    @ignore_warnings
    def test_subset(self):
        test_path = Path("test", "example_test.rb")
        responses.replace(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(get_base_url(), self.organization, self.workspace), json={
            'testPaths': [[{'name': str(test_path)}]],
            'rest': [],
            'subsettingId': 123,
            'summary': {
                'subset': {'duration': 10, 'candidates': 1, 'rate': 100},
                'rest': {'duration': 0, 'candidates': 0, 'rate': 0}
            },
            "isBrainless": False,
        }, status=200)

        result = self.cli('subset', '--target', '20%', '--session', self.session, '--base', str(self.test_files_dir),
                          'minitest', str(self.test_files_dir) + "/test/**/*.rb")

        self.assertEqual(result.exit_code, 0)
        output = Path(self.test_files_dir, "test", "example_test.rb")
        # To ignore "Using 'method_whitelist'..." warning message
        self.assertIn(str(output), result.output.rstrip("\n"))

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_with_invalid_path(self):
        result = self.cli('subset', '--target', '20%', '--session', self.session, '--base', str(self.test_files_dir),
                          'minitest', str(self.test_files_dir) + "/dummy")

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "Error: no tests found matching the path." in result.output)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    @ignore_warnings
    def test_subset_split(self):
        test_path = Path("test", "example_test.rb")
        responses.replace(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(get_base_url(), self.organization, self.workspace), json={
            'testPaths': [[{'name': str(test_path)}]],
            'rest': [],
            'subsettingId': 123,
            'summary': {
                'subset': {'duration': 10, 'candidates': 1, 'rate': 100},
                'rest': {'duration': 0, 'candidates': 0, 'rate': 0}
            },
            "isBrainless": False,
        }, status=200)

        result = self.cli('subset', '--target', '20%', '--session', self.session, '--base', str(self.test_files_dir), '--split',
                          'minitest', str(self.test_files_dir) + "/test/**/*.rb")

        self.assertEqual(result.exit_code, 0)
        # to avoid "Using 'method_whitelist'..." warning message
        self.assertIn('subset/123', result.output.rstrip("\n"))

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    @ignore_warnings
    def test_split_subset(self):
        test_path = Path("test", "example_test.rb")
        responses.replace(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset/456/slice".format(get_base_url(), self.organization, self.workspace),
                          json={'testPaths': [[{'name': str(test_path)}]], 'rest': [], 'subsettingId': 123}, status=200)

        rest = tempfile.NamedTemporaryFile(delete=False)
        result = self.cli('split-subset', '--subset-id', 'subset/456', '--base', str(self.test_files_dir),
                          '--bin', '2/2', '--rest', rest.name, 'minitest')

        self.assertEqual(result.exit_code, 0)
        output = Path(self.test_files_dir, "test", "example_test.rb")
        # To ignore "Using 'method_whitelist'..." warning message
        self.assertIn(str(output), result.output.rstrip("\n"))
        self.assertEqual(rest.read().decode().rstrip("\n"), str(output))
        rest.close()
        os.unlink(rest.name)
