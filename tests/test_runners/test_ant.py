import os
from unittest import mock

import responses  # type: ignore

from tests.cli_test_case import CliTestCase


class AntTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
        result = self.cli('subset', '--target', '10%', '--session',
                          self.session, 'ant', str(self.test_files_dir.joinpath('src').resolve()))
        self.assert_success(result)
        self.assert_subset_payload('subset_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_ant(self):
        result = self.cli('record', 'tests', '--session', self.session,
                          'ant', str(self.test_files_dir) + "/junitreport/TESTS-TestSuites.xml")
        self.assert_success(result)
        self.assert_record_tests_payload("record_test_result.json")
