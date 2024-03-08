import os
from unittest import mock

import responses  # type: ignore

from launchable.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class SubsetTest(CliTestCase):
    mock_json = {
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
    }

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
        responses.replace(responses.GET, "{}/intake/organizations/{}/workspaces/{}/subset/{}".format(
            get_base_url(), self.organization, self.workspace, self.subsetting_id), json=self.mock_json, status=200)

        result = self.cli('inspect', 'subset', '--subset-id', self.subsetting_id, mix_stderr=False)
        expect = """|   Order | Test Path          | In Subset   |   Estimated duration (sec) |
|---------|--------------------|-------------|----------------------------|
|       1 | file=test_file1.py | ✔           |                       1.20 |
|       2 | file=test_file3.py | ✔           |                       0.60 |
|       3 | file=test_file4.py |             |                       1.80 |
|       4 | file=test_file2.py |             |                       0.10 |
"""

        self.assertEqual(result.stdout, expect)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_json_format(self):
        responses.replace(responses.GET, "{}/intake/organizations/{}/workspaces/{}/subset/{}".format(
            get_base_url(), self.organization, self.workspace, self.subsetting_id), json=self.mock_json, status=200)

        result = self.cli('inspect', 'subset', '--subset-id', self.subsetting_id, "--json", mix_stderr=False)
        expect = """{
  "subset": [
    {
      "test_path": "file=test_file1.py",
      "estimated_duration_sec": 1.2
    },
    {
      "test_path": "file=test_file3.py",
      "estimated_duration_sec": 0.6
    }
  ],
  "rest": [
    {
      "test_path": "file=test_file4.py",
      "estimated_duration_sec": 1.8
    },
    {
      "test_path": "file=test_file2.py",
      "estimated_duration_sec": 0.1
    }
  ]
}
"""

        self.assertEqual(result.stdout, expect)
