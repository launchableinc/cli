from pathlib import Path
import responses  # type: ignore
import json
import gzip
import sys
from pathlib import Path
from tests.cli_test_case import CliTestCase
from launchable.utils.http_client import get_base_url


class MinitestTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath(
        '../data/minitest/').resolve()
    result_file_path = test_files_dir.joinpath('record_test_result.json')

    @responses.activate
    def test_record_test_minitest(self):
        result = self.cli('record', 'tests',  '--session',
                          self.session, 'minitest', str(self.test_files_dir) + "/")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            b''.join(responses.calls[0].request.body)).decode())

        expected = self.load_json_from_file(self.result_file_path)
        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    def test_record_test_minitest_chunked(self):
        result = self.cli('record', 'tests',  '--session', self.session, '--post-chunk', 5, 'minitest', str(self.test_files_dir) + "/")
        self.assertEqual(result.exit_code, 0)

        payload1 = json.loads(gzip.decompress(
            b''.join(responses.calls[0].request.body)).decode())
        expected1 = self.load_json_from_file(self.test_files_dir.joinpath('record_test_result_chunk1.json'))

        payload2 = json.loads(gzip.decompress(
            b''.join(responses.calls[1].request.body)).decode())
        expected2 = self.load_json_from_file(self.test_files_dir.joinpath('record_test_result_chunk2.json'))

        # concat 1st and 2nd request for unstable order
        self.assert_json_orderless_equal(expected1['events'] + expected2['events'], payload1['events'] + payload2['events'])

    @responses.activate
    def test_subset(self):
        test_path = Path("test", "example_test.rb")
        responses.replace(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(get_base_url(), self.organization, self.workspace),
                          json={'testPaths': [[{'name': str(test_path)}]]}, status=200)

        result = self.cli('subset', '--target', '20%', '--session', self.session, '--base', str(self.test_files_dir),
                          'minitest', str(self.test_files_dir) + "/test/**/*.rb")

        self.assertEqual(result.exit_code, 0)
        output = Path(self.test_files_dir, "test", "example_test.rb")
        self.assertEqual(result.output.rstrip("\n"), str(output))

    @responses.activate
    def test_subset_with_invalid_path(self):
        result = self.cli('subset', '--target', '20%', '--session', self.session, '--base', str(self.test_files_dir),
                          'minitest', str(self.test_files_dir) + "/dummy")

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "Error: no tests found matching the path." in result.output)
