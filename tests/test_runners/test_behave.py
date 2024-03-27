import os
from unittest import mock

import responses  # type: ignore

from tests.cli_test_case import CliTestCase


class BehaveTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
        pipe = "tutorial.feature"
        result = self.cli('subset', '--target', '10%', '--session', self.session, 'behave', input=pipe)
        self.assert_success(result)
        self.assert_subset_payload('subset_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test(self):
        result = self.cli('record', 'tests', '--session', self.session, 'behave',
                          str(self.test_files_dir) + "/reports/report.xml")
        self.assert_success(result)
        self.assert_record_tests_payload("record_test_result.json")
