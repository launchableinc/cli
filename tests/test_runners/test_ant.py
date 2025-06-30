import os
from unittest import mock

import responses  # type: ignore

from tests.cli_test_case import CliTestCase


class AntTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_subset(self):
        result = self.cli('subset', 'ant', '--session', self.session, '--target',
                          '10%', str(self.test_files_dir.joinpath('src').resolve()))
        self.assert_success(result)
        self.assert_subset_payload('subset_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_test_ant(self):
        result = self.cli('record', 'test', 'ant', '--session', self.session,
                          str(self.test_files_dir) + "/junitreport/TESTS-TestSuites.xml")
        self.assert_success(result)
        self.assert_record_tests_payload("record_test_result.json")
