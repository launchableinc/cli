import os
from unittest import mock

import responses  # type: ignore

from smart_tests.utils.session import read_session, write_build
from tests.cli_test_case import CliTestCase


class GoTestTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_subset_with_session(self):
        pipe = "TestExample1\nTestExample2\nTestExample3\nTestExample4\n" \
               "ok      github.com/launchableinc/rocket-car-gotest      0.268s"
        result = self.cli('subset', 'go-test', '--session', self.session, '--target', '10%', input=pipe)
        self.assert_success(result)
        self.assert_subset_payload('subset_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_subset_without_session(self):
        # emulate launchable record build
        write_build(self.build_name)

        pipe = "TestExample1\nTestExample2\nTestExample3\nTestExample4\n" \
               "ok      github.com/launchableinc/rocket-car-gotest      0.268s"
        result = self.cli('subset', 'go-test', '--target', '10%', input=pipe)

        self.assert_success(result)

        self.assertEqual(read_session(self.build_name), self.session)
        self.assert_subset_payload('subset_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_tests_with_session(self):
        result = self.cli('record', 'test', 'go-test', '--session', self.session,
                          str(self.test_files_dir.joinpath('reportv1')) + "/")
        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_tests_without_session(self):
        # emulate launchable record build
        write_build(self.build_name)

        result = self.cli('record', 'test', 'go-test', str(self.test_files_dir.joinpath('reportv1')) + "/")
        self.assert_success(result)

        self.assertEqual(read_session(self.build_name), self.session)
        self.assert_record_tests_payload('record_test_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_tests_v2(self):
        result = self.cli('record', 'test', 'go-test', '--session', self.session,
                          str(self.test_files_dir.joinpath('reportv2')) + "/")
        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')
