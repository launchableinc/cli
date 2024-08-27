import gzip
import json
import os
import sys
import unittest
from unittest import mock

import responses  # type: ignore

from launchable.commands.record.case_event import CaseEvent
from launchable.testpath import unparse_test_path
from tests.cli_test_case import CliTestCase


class PlaywrightTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ,
                     {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test(self):
        result = self.cli('record', 'tests', '--session', self.session,
                          'playwright', str(self.test_files_dir.joinpath("report.xml")))

        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')

    @unittest.skipIf(
        sys.platform.startswith("win"),
        "The report file contains characters that cannot be handled properly on Windows"
    )
    @responses.activate
    @mock.patch.dict(os.environ,
                     {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_with_json_option(self):
        # report.json was created by `launchableinc/example/playwright`` project
        result = self.cli('record', 'tests', '--session', self.session,
                          'playwright', '--json', str(self.test_files_dir.joinpath("report.json")))

        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result_with_json.json')

    @responses.activate
    @mock.patch.dict(os.environ,
                     {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_timedOut_status(self):
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
        self.cli('record', 'tests', '--session', self.session, 'playwright', str(self.test_files_dir.joinpath("report.xml")))
        xml_payload = json.loads(gzip.decompress(self.find_request('/events').request.body).decode())

        self.assertEqual(_test_test_path_status(xml_payload, target_test_path, CaseEvent.TEST_FAILED), True)

        # JSON Report Case
        self.cli('record', 'tests', '--session', self.session,
                 'playwright', '--json', str(self.test_files_dir.joinpath("report.json")))
        json_payload = json.loads(gzip.decompress(self.find_request('/events', 1).request.body).decode())
        self.assertEqual(_test_test_path_status(json_payload, target_test_path, CaseEvent.TEST_FAILED), True)
