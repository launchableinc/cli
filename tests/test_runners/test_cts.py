import gzip
import json
import os
from pathlib import Path
from unittest import mock

import responses

from launchable.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class CtsTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath('../data/cts/').resolve()
    result_file_path = test_files_dir.joinpath('record_test_result.json')
    subset_result_test_path = test_files_dir.joinpath('subset_result.json')

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
        self.assertEqual(result.exit_code, 0)
        output = "--include-filter \"CtsAbiOverrideHostTestCases[instant]\"\n--include-filter \"CtsAbiOverrideHostTestCases\"\n"
        self.assertEqual(output, result.stdout)
        payload = json.loads(gzip.decompress(responses.calls[0].request.body).decode())
        expected = self.load_json_from_file(self.test_files_dir.joinpath('subset_result.json'))
        self.assert_json_orderless_equal(expected, payload)

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

        self.assertEqual(result.exit_code, 0)
        output = "--exclude-filter \"CtsAbiOverrideHostTestCases[secondary_user]\"\n--exclude-filter \"CtsAbiOverrideHostTestCases\"\n"  # noqa: E501
        self.assertEqual(output, result.stdout)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_tests(self):
        result = self.cli('record', 'tests', '--session', self.session,
                          'cts', str(self.test_files_dir) + "/test_result.xml")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(responses.calls[1].request.body).decode())
        for e in payload["events"]:
            e.pop("created_at", "")

        expected = self.load_json_from_file(self.result_file_path)
        self.assert_json_orderless_equal(expected, payload)
