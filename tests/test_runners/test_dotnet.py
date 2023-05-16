import os
from unittest import mock

import responses  # type: ignore

from launchable.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class DotnetTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
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
        result = self.cli('subset', '--target', '25%', '--session', self.session, 'dotnet')
        self.assertEqual(result.exit_code, 1)

        result = self.cli(
            'subset',
            '--target',
            '25%',
            '--session',
            self.session,
            '--get-tests-from-previous-sessions',
            'dotnet',
            mix_stderr=False)
        self.assertEqual(result.exit_code, 0)

        output = "FullyQualifiedName=rocket_car_dotnet.ExampleTest.TestSub|FullyQualifiedName=rocket_car_dotnet.ExampleTest.TestMul\n"  # noqa: E501
        self.assertEqual(result.output, output)

        result = self.cli(
            'subset',
            '--target',
            '25%',
            '--session',
            self.session,
            '--get-tests-from-previous-sessions',
            '--output-exclusion-rules',
            'dotnet',
            mix_stderr=False)
        self.assertEqual(result.exit_code, 0)
        output = "FullyQualifiedName!=rocket_car_dotnet.ExampleTest.TestAdd&FullyQualifiedName!=rocket_car_dotnet.ExampleTest.TestDiv\n"  # noqa: E501
        self.assertEqual(result.output, output)
