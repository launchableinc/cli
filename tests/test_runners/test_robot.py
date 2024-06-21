import os
from unittest import mock

import responses  # type: ignore

from tests.cli_test_case import CliTestCase


class RobotTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
        result = self.cli('subset', '--target', '10%', '--session',
                          self.session, 'robot', str(self.test_files_dir) + "/dryrun.xml")
        self.assert_success(result)
        self.assert_subset_payload('subset_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test(self):

        result = self.cli('record', 'tests', '--session', self.session,
                          'robot', str(self.test_files_dir) + "/output.xml")
        self.assert_success(result)
        self.assert_record_tests_payload("record_test_result.json")

    # for #637
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_executed_only_one_file(self):

        result = self.cli('record', 'tests', '--session', self.session,
                          'robot', str(self.test_files_dir) + "/single-output.xml")
        self.assert_success(result)
        self.assert_record_tests_payload("record_test_executed_only_one_file_result.json")
