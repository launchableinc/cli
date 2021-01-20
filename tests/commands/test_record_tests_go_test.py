from pathlib import Path
from unittest import mock
import responses
import json
import gzip
from launchable.utils.http_client import get_base_url

from tests.cli_test_case import CliTestCase


class GoTestTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath(
        '../data/go_test/').resolve()

    @mock.patch('requests.request')
    def test_subset_with_session(self, mock_post):
        pipe = "TestExample1\nTestExample2\nTestExample3\nTestExample4\nok      github.com/launchableinc/rocket-car-gotest      0.268s"
        result = self.cli('subset', '--target', '10%',
                          '--session', self.session, 'go-test', input=pipe)
        self.assertEqual(result.exit_code, 0)

        payload = self.gzipped_json_payload(mock_post)
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('subset_result.json'))
        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    def test_subset_without_session(self):
        responses.add(responses.POST, "{}/intake/organizations/launchableinc/workspaces/mothership/builds/{}/test_sessions".format(get_base_url(), self.build_name),
                      json={'id': self.session_id}, status=200)

        responses.add(responses.POST, "{}/intake/organizations/launchableinc/workspaces/mothership/subset".format(get_base_url()),
                      json={'testPaths': []}, status=200)

        pipe = "TestExample1\nTestExample2\nTestExample3\nTestExample4\nok      github.com/launchableinc/rocket-car-gotest      0.268s"
        result = self.cli('subset', '--target', '10%', '--build',
                          self.build_name, 'go-test', input=pipe)

        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[0].request.body).decode())
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('subset_result.json'))
        self.assert_json_orderless_equal(expected, payload)

    @mock.patch('requests.request')
    def test_record_tests_with_session(self, mock_post):
        result = self.cli('record', 'tests',  '--session',
                          self.session, 'go-test', str(self.test_files_dir) + "/")
        self.assertEqual(result.exit_code, 0)

        payload = self.gzipped_json_payload(mock_post)
        # Remove timestamp because it depends on the machine clock
        for c in payload['events']:
            del c['created_at']

        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('record_test_result.json'))
        self.assert_json_orderless_equal(expected, payload)
