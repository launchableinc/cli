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

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
        # cts is required using `--get-tests-from-previous-sessions` option
        result = self.cli("subset", "--target", "30%", "--session", self.session, "cts")
        self.assertEqual(result.exit_code, 1)

        mock_response = {
            "testPaths": [
                [{"type": "Module", "name": "Cts1"}, {"type": "TestCase", "name": "android.example.package1"}],
                [{"type": "Module", "name": "Cts2"}, {"type": "TestCase", "name": "android.example.package2"}],
            ],
            "testRunner": "cts",
            "rest": [
                [{"type": "Module", "name": "Cts3"}, {"type": "TestCase", "name": "android.example.package3"}],
                [{"type": "Module", "name": "Cts4"}, {"type": "TestCase", "name": "android.example.package4"}],
                [{"type": "Module", "name": "Cts5"}, {"type": "TestCase", "name": "android.example.package5"}],
            ],
            "subsettingId": 123,
            "summary": {
                "subset": {"duration": 30, "candidates": 2, "rate": 30},
                "rest": {"duration": 70, "candidates": 3, "rate": 70}
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
            "--get-tests-from-previous-sessions",
            "cts",
            mix_stderr=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout,
                         '--include-filter "Cts1 android.example.package1" --include-filter "Cts2 android.example.package2"\n')

        result = self.cli(
            "subset",
            "--target",
            "30%",
            "--session",
            self.session,
            "--get-tests-from-previous-sessions",
            "--output-exclusion-rules",
            "cts",
            mix_stderr=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.stdout,
            '--exclude-filter "Cts3 android.example.package3" --exclude-filter "Cts4 android.example.package4" --exclude-filter "Cts5 android.example.package5"\n')  # noqa E501

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
