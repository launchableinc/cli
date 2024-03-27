import os
from unittest import mock

import responses  # type: ignore

from tests.cli_test_case import CliTestCase


class CypressTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_cypress(self):
        # test-result.xml was generated used to cypress-io/cypress-example-kitchensink
        # cypress run --reporter junit report.xml
        result = self.cli('record', 'tests', '--session', self.session,
                          'cypress', str(self.test_files_dir) + "/test-result.xml")
        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_cypress(self):
        # test-report.xml is outputed from
        # cypress/integration/examples/window.spec.js, so set it
        pipe = "cypress/integration/examples/window.spec.js"
        result = self.cli('subset', '--target', '10%', '--session', self.session, 'cypress', input=pipe)
        self.assert_success(result)
        self.assert_subset_payload('subset_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_empty_xml(self):
        # parse empty test report XML
        result = self.cli('record', 'tests', '--session', self.session,
                          'cypress', str(self.test_files_dir) + "/empty.xml")
        self.assert_success(result)
        for call in responses.calls:
            self.assertFalse(call.request.url.endswith('/events'), 'there should be no calls to the /events endpoint')
