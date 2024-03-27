import os
from unittest import mock

import responses  # type: ignore

from tests.cli_test_case import CliTestCase


class PlaywrightTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ,
                     {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_rspec(self):
        result = self.cli('record', 'tests', '--session', self.session,
                          'playwright', str(self.test_files_dir.joinpath("report.xml")))

        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')
