from pathlib import Path
from unittest import mock
import responses  # type: ignore
import json
import gzip
import os
from tests.cli_test_case import CliTestCase


class CypressTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath(
        '../data/cypress/').resolve()

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_cypress(self):
        # test-result.xml was generated used to cypress-io/cypress-example-kitchensink
        # cypress run --reporter junit report.xml
        result = self.cli('record', 'tests',  '--session', self.session,
                          'cypress', str(self.test_files_dir) + "/test-result.xml")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[1].request.body).decode())
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('record_test_result.json'))

        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_cypress(self):
        # test-report.xml is outputed from cypress/integration/examples/window.spec.js, so set it
        pipe = "cypress/integration/examples/window.spec.js"
        result = self.cli('subset', '--target', '10%',
                          '--session', self.session, 'cypress', input=pipe)
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[0].request.body).decode())
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('subset_result.json'))
        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_empty_xml(self):
        # parse empty test report XML
        result = self.cli('record', 'tests',  '--session', self.session,
                          'cypress', str(self.test_files_dir) + "/empty.xml")
        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            "close", responses.calls[1].request.url, "No record request")
