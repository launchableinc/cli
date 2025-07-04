import os
from unittest import mock

import responses  # type: ignore

from smart_tests.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class DotnetTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_subset(self):
        mock_response = {
            "testPaths": [
                [
                    {"type": "Assembly", "name": "rocket-car-dotnet.dll"},
                    {"type": "TestSuite", "name": "rocket_car_dotnet"},
                    {"type": "TestSuite", "name": "ExampleTest"},
                    {"type": "TestCase", "name": "TestSub"},
                ],
                [
                    {"type": "Assembly", "name": "rocket-car-dotnet.dll"},
                    {"type": "TestSuite", "name": "rocket_car_dotnet"},
                    {"type": "TestSuite", "name": "ExampleTest"},
                    {"type": "TestCase", "name": "TestMul"},
                ],
            ],
            "rest": [
                [
                    {"type": "Assembly", "name": "rocket-car-dotnet.dll"},
                    {"type": "TestSuite", "name": "rocket_car_dotnet"},
                    {"type": "TestSuite", "name": "ExampleTest"},
                    {"type": "TestCase", "name": "TestAdd"},
                ],
                [
                    {"type": "Assembly", "name": "rocket-car-dotnet.dll"},
                    {"type": "TestSuite", "name": "rocket_car_dotnet"},
                    {"type": "TestSuite", "name": "ExampleTest"},
                    {"type": "TestCase", "name": "TestDiv"},
                ],
            ],
            "testRunner": "dotnet",
            "subsettingId": 123,
            "summary": {
                "subset": {"duration": 25, "candidates": 1, "rate": 25},
                "rest": {"duration": 78, "candidates": 3, "rate": 75}
            },
            "isObservation": False,
        }

        responses.replace(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(
            get_base_url(),
            self.organization,
            self.workspace),
            json=mock_response,
            status=200)

        # dotnet profiles requires Zero Input Subsetting
        result = self.cli('subset', 'dotnet', '--session', self.session_name, '--build', self.build_name, '--target', '25%')
        self.assert_exit_code(result, 1)

        result = self.cli(
            'subset', 'dotnet',
            '--session', self.session_name,
            '--build', self.build_name,
            '--target', '25%',
            '--get-tests-from-previous-sessions',
            mix_stderr=False)
        self.assert_success(result)

        output = "FullyQualifiedName=rocket_car_dotnet.ExampleTest.TestSub|FullyQualifiedName=rocket_car_dotnet.ExampleTest.TestMul\n"  # noqa: E501
        self.assertEqual(result.output, output)

        result = self.cli(
            'subset', 'dotnet',
            '--session', self.session_name,
            '--build', self.build_name,
            '--target', '25%',
            '--get-tests-from-previous-sessions',
            '--output-exclusion-rules',
            mix_stderr=False)
        self.assert_success(result)

        output = "FullyQualifiedName!=rocket_car_dotnet.ExampleTest.TestAdd&FullyQualifiedName!=rocket_car_dotnet.ExampleTest.TestDiv\n"  # noqa: E501
        self.assertEqual(result.output, output)

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_subset_with_bare_option(self):
        mock_response = {
            "testPaths": [
                [
                    {"type": "Assembly", "name": "rocket-car-dotnet.dll"},
                    {"type": "TestSuite", "name": "rocket_car_dotnet"},
                    {"type": "TestSuite", "name": "ExampleTest"},
                    {"type": "TestCase", "name": "TestSub"},
                ],
                [
                    {"type": "Assembly", "name": "rocket-car-dotnet.dll"},
                    {"type": "TestSuite", "name": "rocket_car_dotnet"},
                    {"type": "TestSuite", "name": "ExampleTest"},
                    {"type": "TestCase", "name": "TestMul"},
                ],
            ],
            "rest": [
                [
                    {"type": "Assembly", "name": "rocket-car-dotnet.dll"},
                    {"type": "TestSuite", "name": "rocket_car_dotnet"},
                    {"type": "TestSuite", "name": "ExampleTest"},
                    {"type": "TestCase", "name": "TestAdd"},
                ],
                [
                    {"type": "Assembly", "name": "rocket-car-dotnet.dll"},
                    {"type": "TestSuite", "name": "rocket_car_dotnet"},
                    {"type": "TestSuite", "name": "ExampleTest"},
                    {"type": "TestCase", "name": "TestDiv"},
                ],
            ],
            "testRunner": "dotnet",
            "subsettingId": 123,
            "summary": {
                "subset": {"duration": 25, "candidates": 1, "rate": 25},
                "rest": {"duration": 78, "candidates": 3, "rate": 75}
            },
            "isObservation": False,
        }

        responses.replace(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(
            get_base_url(),
            self.organization,
            self.workspace),
            json=mock_response,
            status=200)

        result = self.cli(
            'subset', 'dotnet',
            '--session', self.session_name,
            '--build', self.build_name,
            '--target', '25%',
            '--get-tests-from-previous-sessions',
            '--bare',
            mix_stderr=False)
        self.assert_success(result)

        output = "rocket_car_dotnet.ExampleTest.TestSub\nrocket_car_dotnet.ExampleTest.TestMul\n"
        self.assertEqual(result.output, output)

        result = self.cli(
            'subset', 'dotnet',
            '--session', self.session_name,
            '--build', self.build_name,
            '--target', '25%',
            '--get-tests-from-previous-sessions',
            '--output-exclusion-rules',
            '--bare',
            mix_stderr=False)
        self.assert_success(result)

        output = "rocket_car_dotnet.ExampleTest.TestAdd\nrocket_car_dotnet.ExampleTest.TestDiv\n"
        self.assertEqual(result.output, output)

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_tests(self):
        result = self.cli('record', 'test', 'dotnet', '--session', self.session_name, '--build',
                          self.build_name, str(self.test_files_dir) + "/test-result.xml")
        self.assert_success(result)
        self.assert_record_tests_payload("record_test_result.json")
