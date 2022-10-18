import os
import tempfile
from unittest import mock

import responses
from launchable.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class SplitSubsetTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_split_subset_with_observation_mode(self):
        pipe = "test_1.py\ntest_2.py\ntest_3.py\ntest_4.py\ntest_5.py\ntest_6.py"
        mock_json_response = {
            "testPaths": [
                [{"type": "file", "name": "test_1.py"}],
                [{"type": "file", "name": "test_3.py"}],

            ],
            "rest": [
                [{"type": "file", "name": "test_5.py"}],

            ],
            "subsettingId": 456,
            "isObservation": False,
        }

        responses.replace(
            responses.POST,
            "{}/intake/organizations/{}/workspaces/{}/subset/{}/slice".format(
                get_base_url(),
                self.organization,
                self.workspace,
                self.subsetting_id),
            json=mock_json_response,
            status=200)

        rest = tempfile.NamedTemporaryFile(delete=False)
        result = self.cli("split-subset", "--subset-id", "subset/456", "--bin", "1/2", "--rest",
                          rest.name, "file", mix_stderr=False, input=pipe)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.stdout, "test_1.py\ntest_3.py\n")
        self.assertEqual(
            rest.read().decode(), os.linesep.join(["test_5.py"]))
        rest.close()
        os.unlink(rest.name)

        mock_json_response["isObservation"] = True
        responses.replace(
            responses.POST,
            "{}/intake/organizations/{}/workspaces/{}/subset/{}/slice".format(
                get_base_url(),
                self.organization,
                self.workspace,
                self.subsetting_id),
            json=mock_json_response,
            status=200)

        observation_mode_rest = tempfile.NamedTemporaryFile(delete=False)
        result = self.cli("split-subset", "--subset-id", "subset/456", "--bin", "1/2", "--rest",
                          observation_mode_rest.name, "file", mix_stderr=False, input=pipe)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.stdout, "test_1.py\ntest_3.py\ntest_5.py\n")
        self.assertEqual(
            observation_mode_rest.read().decode(), os.linesep.join(["test_5.py"]))
        observation_mode_rest.close()
        os.unlink(observation_mode_rest.name)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_split_subset(self):
        pipe = "test_1.py\ntest_2.py\ntest_3.py\ntest_4.py\ntest_5.py\ntest_6.py"
        mock_json_response = {
            "testPaths": [
                [{"type": "file", "name": "test_1.py"}],
                [{"type": "file", "name": "test_6.py"}],
            ],
            "rest": [],
            "subsettingId": 456,
            "isObservation": False,
        }

        responses.replace(
            responses.POST,
            "{}/intake/organizations/{}/workspaces/{}/subset/{}/slice".format(
                get_base_url(),
                self.organization,
                self.workspace,
                self.subsetting_id),
            json=mock_json_response,
            status=200)

        result = self.cli(
            "split-subset",
            "--subset-id",
            "subset/456",
            "--bin",
            "1/2",
            "file",
            mix_stderr=False,
            input=pipe,
        )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, "test_1.py\ntest_6.py\n")
