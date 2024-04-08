import os
import sys
import unittest
from unittest import mock

import responses  # type: ignore

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
