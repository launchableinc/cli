from pathlib import Path
import responses  # type: ignore
import json
import gzip
import os
from launchable.utils.session import read_session
from tests.cli_test_case import CliTestCase
from unittest import mock


class GoTestTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath(
        '../data/go_test/').resolve()

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_with_session(self):
        pipe = "TestExample1\nTestExample2\nTestExample3\nTestExample4\nok      github.com/launchableinc/rocket-car-gotest      0.268s"
        result = self.cli('subset', '--target', '10%',
                          '--session', self.session, 'go-test', input=pipe)
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[0].request.body).decode())
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('subset_result.json'))
        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_without_session(self):
        pipe = "TestExample1\nTestExample2\nTestExample3\nTestExample4\nok      github.com/launchableinc/rocket-car-gotest      0.268s"
        result = self.cli('subset', '--target', '10%', '--build',
                          self.build_name, 'go-test', input=pipe)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(read_session(self.build_name), self.session)

        payload = json.loads(gzip.decompress(
            responses.calls[1].request.body).decode())
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('subset_result.json'))
        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_tests_with_session(self):
        result = self.cli('record', 'tests',  '--session',
                          self.session, 'go-test', str(self.test_files_dir) + "/")
        self.assertEqual(result.exit_code, 0)

        self.assertIn(
            'events', responses.calls[1].request.url, 'call events API')
        payload = json.loads(gzip.decompress(responses.calls[1].request.body).decode())
        # Remove timestamp because it depends on the machine clock
        for c in payload['events']:
            del c['created_at']

        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('record_test_result.json'))
        self.assert_json_orderless_equal(expected, payload)

        self.assertIn(
            'close', responses.calls[2].request.url, 'call close API')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_tests_without_session(self):
        result = self.cli('record', 'tests', '--build',
                          self.build_name, 'go-test', str(self.test_files_dir) + "/")
        self.assertEqual(result.exit_code, 0)

        self.assertEqual(read_session(self.build_name), self.session)

        self.assertIn(
            'events', responses.calls[2].request.url, 'call events API')
        payload = json.loads(gzip.decompress(responses.calls[2].request.body).decode())
        for c in payload['events']:
            del c['created_at']

        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('record_test_result.json'))
        self.assert_json_orderless_equal(expected, payload)

        self.assertIn(
            'close', responses.calls[3].request.url, 'call close API')
