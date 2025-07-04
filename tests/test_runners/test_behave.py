import os
from unittest import mock

import responses  # type: ignore

from tests.cli_test_case import CliTestCase


class BehaveTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_subset(self):
        pipe = "tutorial.feature"
        result = self.cli(
            'subset',
            'behave',
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
    def test_record_test(self):
        result = self.cli('record', 'test', 'behave', '--session', self.session_name, '--build', self.build_name,
                          str(self.test_files_dir) + "/reports/report.xml")
        self.assert_success(result)
        self.assert_record_tests_payload("record_test_result.json")
