from pathlib import Path
from unittest import mock

from tests.cli_test_case import CliTestCase

class GoTestTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath('../data/go_test/').resolve()

    @mock.patch('requests.request')
    def test_subset(self, mock_post):
        pipe = "TestExample1\nTestExample2\nTestExample3\nTestExample4\nok      github.com/launchableinc/rocket-car-gotest      0.268s"
        result=self.cli('subset', '--target', '10%', '--session', self.session, 'go-test', input=pipe)
        self.assertEqual(result.exit_code, 0)

        payload = self.gzipped_json_payload(mock_post)
        expected = self.load_json_from_file(self.test_files_dir.joinpath('subset_result.json'))
        self.assert_json_orderless_equal(expected, payload)

    @mock.patch('requests.request')
    def test_record_tests(self, mock_post):
        result=self.cli('record', 'tests',  '--session', self.session, 'go-test', str(self.test_files_dir) + "/")
        self.assertEqual(result.exit_code, 0)

        payload = self.gzipped_json_payload(mock_post)
        # Remove timestamp because it depends on the machine clock
        for c in payload['events']:
            del c['created_at']

        expected = self.load_json_from_file(self.test_files_dir.joinpath('record_test_result.json'))
        self.assert_json_orderless_equal(expected, payload)
