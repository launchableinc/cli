from pathlib import Path
from unittest import mock
import responses
import json
import gzip
from tests.cli_test_case import CliTestCase


class GradleTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath('../data/gradle/recursion').resolve()
    result_file_path = test_files_dir.joinpath('expected.json')

    @responses.activate
    def test_record_test_gradle(self):
        result = self.cli('record', 'tests',  '--session', self.session, 'gradle', str(self.test_files_dir) + "/**/reports")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            b''.join(responses.calls[0].request.body)).decode())

        expected = self.load_json_from_file(self.result_file_path)
        self.assert_json_orderless_equal(expected, payload)
