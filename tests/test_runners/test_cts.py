import os
from unittest import mock

import responses

from launchable.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class CtsTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
        pipe = """ # noqa: E501
==================
Notice:
We collect anonymous usage statistics in accordance with our Content Licenses (https://source.android.com/setup/start/licenses), Contributor License Agreement (https://opensource.google.com/docs/cla/), Privacy Policy (https://policies.google.com/privacy) and Terms of Service (https://policies.google.com/terms).
==================
Android Compatibility Test Suite 12.1_r5 (9566553)
Use "help" or "help all" to get more information on running commands.
Non-interactive mode: Running initial command then exiting.
Using commandline arguments as starting command: [list, modules]
arm64-v8a CtsAbiOverrideHostTestCases[instant]
arm64-v8a CtsAbiOverrideHostTestCases[secondary_user]
arm64-v8a CtsAbiOverrideHostTestCases
armeabi-v7a CtsAbiOverrideHostTestCases
        """

        mock_response = {
            "testPaths": [
                [{"type": "Module", "name": "CtsAbiOverrideHostTestCases[instant]"}],
                [{"type": "Module", "name": "CtsAbiOverrideHostTestCases"}],

            ],
            "testRunner": "cts",
            "rest": [
                [{"type": "Module", "name": "CtsAbiOverrideHostTestCases[secondary_user]"}],
                [{"type": "Module", "name": "CtsAbiOverrideHostTestCases"}],
            ],
            "subsettingId": 123,
            "summary": {
                "subset": {"duration": 30, "candidates": 2, "rate": 30},
                "rest": {"duration": 70, "candidates": 2, "rate": 70}
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
            "subset",
            "--target",
            "30%",
            "--session",
            self.session,
            "cts",
            input=pipe,
            mix_stderr=False)
        self.assert_success(result)

        output = "--include-filter \"CtsAbiOverrideHostTestCases[instant]\"\n--include-filter \"CtsAbiOverrideHostTestCases\"\n"
        self.assertEqual(output, result.stdout)
        self.assert_subset_payload('subset_result.json')

        result = self.cli(
            "subset",
            "--target",
            "30%",
            "--session",
            self.session,
            "--output-exclusion-rules",
            "cts",
            input=pipe,
            mix_stderr=False)

        self.assert_success(result)

        output = "--exclude-filter \"CtsAbiOverrideHostTestCases[secondary_user]\"\n--exclude-filter \"CtsAbiOverrideHostTestCases\"\n"  # noqa: E501
        self.assertEqual(output, result.stdout)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_tests(self):
        result = self.cli('record', 'tests', '--session', self.session,
                          'cts', str(self.test_files_dir) + "/test_result.xml")
        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')
