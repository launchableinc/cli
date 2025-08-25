import os
from unittest import TestCase, mock

import responses  # type: ignore

from smart_tests.test_runners.prove import remove_leading_number_and_dash
from smart_tests.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class remove_leading_number_and_dash_Test(TestCase):
    def test_remove_leading_number_and_dash(self):
        self.assertEqual(
            remove_leading_number_and_dash(input_string="1 - add"),
            "add",
        )
        self.assertEqual(
            remove_leading_number_and_dash(input_string="3 - add"),
            "add",
        )
        self.assertEqual(
            remove_leading_number_and_dash(input_string="100 - add"),
            "add",
        )
        self.assertEqual(
            remove_leading_number_and_dash(input_string="1 - 1 - add"),
            "1 - add",
        )


class ProveTestTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_tests(self):
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

        result = self.cli('record', 'test', 'prove', '--build', self.build_name, '--session', self.session_name,
                          str(self.test_files_dir.joinpath('report.xml')))
        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')
