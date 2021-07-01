from pathlib import Path
import responses  # type: ignore
import json
import gzip
import os
from unittest import mock
from tests.cli_test_case import CliTestCase


class PytestTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath('../data/pytest/').resolve()
    result_file_path = test_files_dir.joinpath('record_test_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
        result = self.cli('subset', '--target', '10%', '--session',
                          self.session, 'pytest', "tests")
        self.assertEqual(result.exit_code, 0)
        payload = json.loads(gzip.decompress(
            responses.calls[0].request.body).decode())
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('subset_result.json'))

        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_pytest(self):
        result = self.cli('record', 'tests',  '--session', self.session,
                          'pytest', str(self.test_files_dir.joinpath("report.xml")))

        self.assertEqual(result.exit_code, 0)
        payload = json.loads(gzip.decompress(responses.calls[1].request.body).decode())
        expected = self.load_json_from_file(self.result_file_path)
        self.assert_json_orderless_equal(expected, payload)

    def setUp(self):
        super().setUp()
        self.current_dir = os.getcwd();
        os.chdir(str(self.test_files_dir))

    def tearDown(self):
        os.chdir(self.current_dir)
        super().tearDown()
