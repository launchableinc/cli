from pathlib import Path
from unittest import mock

from tests.cli_test_case import CliTestCase


class GoogleTestTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath(
        '../data/googletest/').resolve()
    result_file_path = test_files_dir.joinpath('record_test_result.json')

    @mock.patch('requests.request')
    def test_record_test_googletest(self, mock_post):
        result = self.cli('record', 'tests',  '--session', self.session,
                          'googletest', str(self.test_files_dir) + "/")
        self.assertEqual(result.exit_code, 0)

        payload = self.gzipped_json_payload(mock_post)
        expected = self.load_json_from_file(self.result_file_path)

        self.assert_json_orderless_equal(expected, payload)
