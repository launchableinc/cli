from pathlib import Path
import responses # type: ignore
import json
import gzip
import sys
from tests.cli_test_case import CliTestCase


class RspecTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath('../data/rspec/').resolve()
    result_file_path = test_files_dir.joinpath('record_test_result.json')

    @responses.activate
    def test_record_test_rspec(self):
        result = self.cli('record', 'tests',  '--session', self.session, 'rspec', str(self.test_files_dir.joinpath("rspec.xml")))
        self.assertEqual(result.exit_code, 0)
        payload = json.loads(gzip.decompress(
            b''.join(responses.calls[0].request.body)).decode())
        expected = self.load_json_from_file(self.result_file_path)
        self.assert_json_orderless_equal(expected, payload)
