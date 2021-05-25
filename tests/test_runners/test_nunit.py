from pathlib import Path
import responses  # type: ignore
import json
import gzip
from tests.cli_test_case import CliTestCase


class NUnitTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath('../data/nunit/').resolve()

    @responses.activate
    def test_subset(self):
        result = self.cli('subset', '--target', '10%', '--session', self.session,
                          'nunit', str(self.test_files_dir) + "/list.xml")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[0].request.body).decode())

        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('subset_result.json'))

        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    def test_record_test(self):
        result = self.cli('record', 'tests',  '--session', self.session,
                          'nunit', str(self.test_files_dir) + "/output.xml")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            b''.join(responses.calls[1].request.body)).decode())

        expected = self.load_json_from_file(
            self.test_files_dir.joinpath("record_test_result.json"))

        self.assert_json_orderless_equal(expected, payload)
