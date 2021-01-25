from pathlib import Path
from unittest import mock

from tests.cli_test_case import CliTestCase


class CypressTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath(
        '../data/cypress/').resolve()

    @mock.patch('requests.request')
    def test_record_test_cypress(self, mock_post):
        # test-result.xml was generated used to cypress-io/cypress-example-kitchensink
        # cypress run --reporter junit report.xml
        result = self.cli('record', 'tests',  '--session', self.session,
                          'cypress', str(self.test_files_dir) + "/test-result.xml")
        self.assertEqual(result.exit_code, 0)

        payload = self.gzipped_json_payload(mock_post)
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('record_test_result.json'))

        self.assert_json_orderless_equal(expected, payload)

    @mock.patch('requests.request')
    def test_subset_cypress(self, mock_post):
        # test-report.xml is outputed from cypress/integration/examples/window.spec.js, so set it
        pipe = "cypress/integration/examples/window.spec.js"
        result = self.cli('subset', '--target', '10%',
                          '--session', self.session, 'cypress', input=pipe)
        self.assertEqual(result.exit_code, 0)

        payload = self.gzipped_json_payload(mock_post)
        print("fooo")
        print(payload)
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('subset_result.json'))
        self.assert_json_orderless_equal(expected, payload)
