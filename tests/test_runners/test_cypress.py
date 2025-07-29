import os
from unittest import mock

import responses  # type: ignore

from smart_tests.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class CypressTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_test_cypress(self):
        # Override session name lookup to allow session resolution
        responses.replace(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/"
            f"{self.workspace}/builds/{self.build_name}/test_session_names/{self.session_name}",
            json={
                'id': self.session_id,
                'isObservation': False,
            },
            status=200)

        # test-result.xml was generated used to cypress-io/cypress-example-kitchensink
        # cypress run --reporter junit report.xml
        result = self.cli('record', 'test', 'cypress', '--session', self.session_name, '--build', self.build_name,
                          str(self.test_files_dir) + "/test-result.xml")
        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_subset_cypress(self):
        # Override session name lookup to allow session resolution
        responses.replace(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/"
            f"{self.workspace}/builds/{self.build_name}/test_session_names/{self.session_name}",
            json={
                'id': self.session_id,
                'isObservation': False,
            },
            status=200)

        # test-report.xml is outputed from
        # cypress/integration/examples/window.spec.js, so set it
        pipe = "cypress/integration/examples/window.spec.js"
        result = self.cli(
            'subset',
            'cypress',
            '--session',
            self.session_name,
            '--build',
            self.build_name,
            '--target',
            '10%',
            input=pipe)
        self.assert_success(result)
        self.assert_subset_payload('subset_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_empty_xml(self):
        # Override session name lookup to allow session resolution
        responses.replace(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/"
            f"{self.workspace}/builds/{self.build_name}/test_session_names/{self.session_name}",
            json={
                'id': self.session_id,
                'isObservation': False,
            },
            status=200)

        # parse empty test report XML
        result = self.cli('record', 'test', 'cypress', '--session', self.session_name, '--build', self.build_name,
                          str(self.test_files_dir) + "/empty.xml")
        self.assert_success(result)
        for call in responses.calls:
            self.assertFalse(call.request.url.endswith('/events'), 'there should be no calls to the /events endpoint')
