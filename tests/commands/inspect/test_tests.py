import os
import responses  # type: ignore
from unittest import mock
from tests.cli_test_case import CliTestCase
from launchable.utils.http_client import get_base_url


class SubsetTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
        test_session_id = 16
        responses.replace(responses.GET, "{}/intake/organizations/{}/workspaces/{}/test_sessions/{}/events".format(
            get_base_url(), self.organization, self.workspace, test_session_id), json=[
                {"testPath": [
                    {"type": "file", "name": "test_file1.py"}], "duration": 1.2, "stderr": "", "stdout": "", "createdAt":  "2021-01-02T03:04:05.000+00:00", "status": "SUCCESS"},
                {"testPath": [
                    {"type": "file", "name": "test_file3.py"}], "duration": 0.6,  "stderr": "", "stdout": "", "createdAt":  "2021-01-02T03:04:05.000+00:00", "status": "SUCCESS"},


                {"testPath": [
                    {"type": "file", "name": "test_file4.py"}], "duration": 1.8,  "stderr": "", "stdout": "", "createdAt":  "2021-01-02T03:04:05.000+00:00", "status": "FAILURE"},
                {"testPath": [
                    {"type": "file", "name": "test_file2.py"}], "duration": 0.1,  "stderr": "", "stdout": "", "createdAt":  "2021-01-02T03:04:05.000+00:00", "status": "FAILURE"},
        ], status=200)

        result = self.cli('inspect', 'tests', '--test-session-id',
                          test_session_id, mix_stderr=False)
        expect = """| Test Path          |   Duration (sec) | Status   | Uploaded At                   |
|--------------------|------------------|----------|-------------------------------|
| file=test_file1.py |              1.2 | SUCCESS  | 2021-01-02T03:04:05.000+00:00 |
| file=test_file3.py |              0.6 | SUCCESS  | 2021-01-02T03:04:05.000+00:00 |
| file=test_file4.py |              1.8 | FAILURE  | 2021-01-02T03:04:05.000+00:00 |
| file=test_file2.py |              0.1 | FAILURE  | 2021-01-02T03:04:05.000+00:00 |
"""

        self.assertEqual(result.stdout, expect)
