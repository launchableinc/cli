import os
from unittest import mock

import responses  # type: ignore

from tests.cli_test_case import CliTestCase


class RspecTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ,
                     {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_test_rspec(self):
        result = self.cli('record', 'test', 'rspec', '--session', self.session_name, '--build', self.build_name,
                          str(self.test_files_dir.joinpath("rspec.xml")))
        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')
