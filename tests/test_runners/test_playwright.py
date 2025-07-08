import gzip
import json
import os
import sys
import unittest
from unittest import mock

import responses  # type: ignore

from smart_tests.commands.record.case_event import CaseEvent
from smart_tests.testpath import unparse_test_path
from smart_tests.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class PlaywrightTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ,
                     {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_test(self):
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

        result = self.cli('record', 'test', 'playwright', '--session', self.session_name, '--build', self.build_name,
                          str(self.test_files_dir.joinpath("report.xml")))

        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')

    @unittest.skipIf(
        sys.platform.startswith("win"),
        "The report file contains characters that cannot be handled properly on Windows"
    )
    @responses.activate
    @mock.patch.dict(os.environ,
                     {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_test_with_json_option(self):
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

        # report.json was created by `launchableinc/example/playwright`` project
        result = self.cli('record', 'test', 'playwright', '--session', self.session_name, '--build', self.build_name,
                          '--json', str(self.test_files_dir.joinpath("report.json")))

        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result_with_json.json')

    @responses.activate
    @mock.patch.dict(os.environ,
                     {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_test_timedOut_status(self):
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

        def _test_test_path_status(payload, test_path: str, status: CaseEvent) -> bool:
            checked = False
            for event in payload.get("events"):
                if unparse_test_path(event.get("testPath")) != test_path:
                    continue
                self.assertEqual(event.get("status"), status)
                checked = True
            return checked

        target_test_path = "file=tests/timeout-example.spec.ts#testcase=time-out"

        # XML Report Case
        self.cli('record', 'test', 'playwright', '--session', self.session_name, '--build',
                 self.build_name, str(self.test_files_dir.joinpath("report.xml")))
        xml_payload = json.loads(gzip.decompress(self.find_request('/events').request.body).decode())

        self.assertEqual(_test_test_path_status(xml_payload, target_test_path, CaseEvent.TEST_FAILED), True)

        # JSON Report Case
        self.cli('record', 'test', 'playwright', '--session', self.session_name, '--build', self.build_name,
                 '--json', str(self.test_files_dir.joinpath("report.json")))
        json_payload = json.loads(gzip.decompress(self.find_request('/events', 1).request.body).decode())
        self.assertEqual(_test_test_path_status(json_payload, target_test_path, CaseEvent.TEST_FAILED), True)
