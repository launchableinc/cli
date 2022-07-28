import os
import tempfile
from unittest import mock
import responses
from launchable.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class SubsetTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_with_observation_mode(self):

        pipe = "test_1.py\ntest_2.py\ntest_3.py\ntest_4.py"
        mock_json_response = {
            "testPaths": [
                [{"type": "file", "name": "test_1.py"}],
                [{"type": "file", "name": "test_2.py"}],

            ],
            "rest": [
                [{"type": "file", "name": "test_3.py"}],
                [{"type": "file", "name": "test_4.py"}],

            ],
            "subsettingId": 123,
            "summary": {
                "subset": {"duration": 10, "candidates": 3, "rate": 50},
                "rest": {"duration": 10, "candidates": 3, "rate": 50}
            },
            "isObservation": False,
        }
        responses.replace(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(get_base_url(), self.organization, self.workspace),
                          json=mock_json_response, status=200)

        rest = tempfile.NamedTemporaryFile(delete=False)
        result = self.cli("subset", "--target", "30%", "--session",
                          self.session, "--rest", rest.name,   "file", mix_stderr=False, input=pipe)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.stdout, "test_1.py\ntest_2.py\n")
        self.assertEqual(
            rest.read().decode(), os.linesep.join(["test_3.py", "test_4.py"]))
        rest.close()
        os.unlink(rest.name)

        mock_json_response["isObservation"] = True
        responses.replace(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(get_base_url(), self.organization, self.workspace),
                          json=mock_json_response, status=200)

        observation_mode_rest = tempfile.NamedTemporaryFile(delete=False)
        result = self.cli("subset", "--target", "30%", "--session",
                          self.session, "--rest", observation_mode_rest.name, "--observation", "file", input=pipe, mix_stderr=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.stdout, "test_1.py\ntest_2.py\ntest_3.py\ntest_4.py\n")
        self.assertEqual(
            observation_mode_rest.read().decode(), os.linesep.join(["test_3.py", "test_4.py"]))
        observation_mode_rest.close()
        os.unlink(observation_mode_rest.name)
