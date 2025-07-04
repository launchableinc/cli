import os
from unittest import mock

import responses  # type: ignore

from smart_tests.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class NUnitTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_subset(self):
        responses.replace(
            responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(
                get_base_url(), self.organization, self.workspace), json={
                'testPaths': [
                    [
                        {
                            "type": "Assembly",
                            "name": "calc.dll",
                        },
                        {
                            "type": "TestSuite",
                            "name": "ParameterizedTests",
                        },
                        {
                            "type": "TestFixture",
                            "name": "MyTests",
                        },
                        {
                            "type": "ParameterizedMethod",
                            "name": "DivideTest",
                        },
                        {
                            "type": "TestCase",
                            "name": "DivideTest(12,3)",
                        },
                    ],
                    [
                        {
                            "type": "Assembly",
                            "name": "calc.dll",
                        },
                        {
                            "type": "TestSuite",
                            "name": "calc",
                        },
                        {
                            "type": "TestFixture",
                            "name": "Tests1",
                        },
                        {
                            "type": "TestCase",
                            "name": "Test1",
                        },
                    ],
                ],
                'rest': [],
                'subsettingId': 123,
                'summary': {
                    'subset': {
                        'duration': 15,
                        'candidates': 2,
                        'rate': 100,
                    },
                    'rest': {
                        'duration': 0,
                        'candidates': 0,
                        'rate': 0,
                    },
                },
            }, status=200)

        result = self.cli('subset', 'nunit', '--session', self.session_name, '--build', self.build_name, '--target', '10%',
                          str(self.test_files_dir) + "/list.xml")
        self.assert_success(result)
        self.assert_subset_payload('subset_result.json')

        output = 'ParameterizedTests.MyTests.DivideTest(12,3)\ncalc.Tests1.Test1'
        self.assertIn(output, result.output)

    @responses.activate
    @mock.patch.dict(os.environ,
                     {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_test_on_linux(self):
        result = self.cli('record', 'test', 'nunit', '--session', self.session_name, '--build',
                          self.build_name, str(self.test_files_dir) + "/output-linux.xml")
        self.assert_success(result)
        self.assert_record_tests_payload("record_test_result-linux.json")

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_test_on_windows(self):
        result = self.cli('record', 'test', 'nunit', '--session', self.session_name, '--build',
                          self.build_name, str(self.test_files_dir) + "/output-windows.xml")
        self.assert_success(result)
        self.assert_record_tests_payload("record_test_result-windows.json")

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_test_with_nunit_reporter_bug(self):
        result = self.cli('record', 'test', 'nunit', '--session', self.session_name, '--build', self.build_name,
                          str(self.test_files_dir) + "/nunit-reporter-bug-with-nested-type.xml")
        self.assert_success(result)
        # turns out we collapse all TestFixtures to TestSuitest so the golden file has TestSuite=Outer+Inner,
        # not TestFixture=Outer+Inner
        self.assert_record_tests_payload("nunit-reporter-bug-with-nested-type.json")
