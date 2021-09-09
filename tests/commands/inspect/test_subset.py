import os
import responses  # type: ignore
from unittest import mock
from tests.cli_test_case import CliTestCase
from launchable.utils.http_client import get_base_url


class SubsetTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
        subset_id = 456
        responses.replace(responses.GET, "{}/intake/organizations/{}/workspaces/{}/subset/{}".format(
            get_base_url(), self.organization, self.workspace, subset_id), json={
            "testPaths": [
                {"testPath": [
                    {"type": "file", "name": "test_file1.py"}], "duration": 1200},
                {"testPath": [
                    {"type": "file", "name": "test_file3.py"}], "duration": 600},
            ],
            "rest": [
                {"testPath": [
                    {"type": "file", "name": "test_file4.py"}], "duration": 1800},
                {"testPath": [
                    {"type": "file", "name": "test_file2.py"}], "duration": 100}

            ]
        }, status=200)

        result = self.cli('inspect', 'subset', '--subset-id',
                          subset_id, mix_stderr=False)
        expect = """|   Order | Test Path          | In Subset   |   Estimated duration (sec) |
|---------|--------------------|-------------|----------------------------|
|       1 | file=test_file1.py | ✔           |                        1.2 |
|       2 | file=test_file3.py | ✔           |                        0.6 |
|       3 | file=test_file4.py |             |                        1.8 |
|       4 | file=test_file2.py |             |                        0.1 |
"""

        self.assertEqual(result.stdout, expect)
