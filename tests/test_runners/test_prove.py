import os
from unittest import TestCase, mock

import responses  # type: ignore

from launchable.test_runners.prove import remove_leading_number_and_dash
from launchable.utils.session import read_session, write_build
from tests.cli_test_case import CliTestCase


class remove_leading_number_and_dash_Test(TestCase):
    def test_remove_leading_number_and_dash(self):
        self.assertEqual(
            remove_leading_number_and_dash(input_string="1 - add"),
            "add",
        )
        self.assertEqual(
            remove_leading_number_and_dash(input_string="3 - add"),
            "add",
        )
        self.assertEqual(
            remove_leading_number_and_dash(input_string="100 - add"),
            "add",
        )
        self.assertEqual(
            remove_leading_number_and_dash(input_string="1 - 1 - add"),
            "1 - add",
        )


class ProveTestTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_tests(self):
        # emulate launchable record build
        write_build(self.build_name)

        result = self.cli('record', 'tests', 'prove', str(self.test_files_dir.joinpath('report.xml')))
        self.assert_success(result)

        self.assertEqual(read_session(self.build_name), self.session)
        self.assert_record_tests_payload('record_test_result.json')
