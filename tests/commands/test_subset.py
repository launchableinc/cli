import gzip
import json
import os
import tempfile
from unittest import mock

import responses  # type: ignore

from launchable.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class SubsetTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
        pipe = "test_1.py\ntest_2.py\ntest_3.py\ntest_4.py"
        mock_json_response = {
            "testPaths": [
                [{"type": "file", "name": "test_1.py"}],
                [{"type": "file", "name": "test_2.py"}],

            ],
            "testRunner": "file",
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
        responses.replace(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(
            get_base_url(),
            self.organization,
            self.workspace),
            json=mock_json_response,
            status=200)

        rest = tempfile.NamedTemporaryFile(delete=False)
        result = self.cli("subset", "--target", "30%", "--session",
                          self.session, "--rest", rest.name, "file", mix_stderr=False, input=pipe)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, "test_1.py\ntest_2.py\n")
        self.assertEqual(rest.read().decode(), os.linesep.join(["test_3.py", "test_4.py"]))
        rest.close()
        os.unlink(rest.name)

        # case: rest is empty
        mock_json_response = {
            "testPaths": [
                [{"type": "file", "name": "test_1.py"}],
                [{"type": "file", "name": "test_2.py"}],
                [{"type": "file", "name": "test_3.py"}],
                [{"type": "file", "name": "test_4.py"}],
            ],
            "testRunner": "file",
            "rest": [],
            "subsettingId": 123,
            "summary": {
                "subset": {"duration": 10, "candidates": 3, "rate": 50},
                "rest": {"duration": 10, "candidates": 3, "rate": 50}
            },
            "isObservation": False,
        }
        responses.replace(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(
            get_base_url(),
            self.organization,
            self.workspace),
            json=mock_json_response,
            status=200)

        rest = tempfile.NamedTemporaryFile(delete=False)
        result = self.cli("subset", "--target", "30%", "--session",
                          self.session, "--rest", rest.name, "file", mix_stderr=False, input=pipe)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, "test_1.py\ntest_2.py\ntest_3.py\ntest_4.py\n")
        self.assertEqual(rest.read().decode(), "")
        rest.close()
        os.unlink(rest.name)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_with_observation_mode(self):
        pipe = "test_1.py\ntest_2.py\ntest_3.py\ntest_4.py"
        mock_json_response = {
            "testPaths": [
                [{"type": "file", "name": "test_1.py"}],
                [{"type": "file", "name": "test_2.py"}],
            ],
            "testRunner": "file",
            "rest": [
                [{"type": "file", "name": "test_3.py"}],
                [{"type": "file", "name": "test_4.py"}],

            ],
            "subsettingId": 123,
            "summary": {
                "subset": {"duration": 10, "candidates": 3, "rate": 50},
                "rest": {"duration": 10, "candidates": 3, "rate": 50}
            },
            "isObservation": True,
        }

        responses.replace(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(
            get_base_url(),
            self.organization,
            self.workspace),
            json=mock_json_response,
            status=200)

        observation_mode_rest = tempfile.NamedTemporaryFile(delete=False)
        result = self.cli(
            "subset",
            "--target",
            "30%",
            "--session",
            self.session,
            "--rest",
            observation_mode_rest.name,
            "--observation",
            "file",
            input=pipe,
            mix_stderr=False)
        self.assertEqual(result.exit_code, 0)

        self.assertEqual(result.stdout, "test_1.py\ntest_2.py\ntest_3.py\ntest_4.py\n")
        self.assertEqual(observation_mode_rest.read().decode(), "")
        observation_mode_rest.close()
        os.unlink(observation_mode_rest.name)

        # case: rest is empty
        mock_json_response = {
            "testPaths": [
                [{"type": "file", "name": "test_1.py"}],
                [{"type": "file", "name": "test_2.py"}],
                [{"type": "file", "name": "test_3.py"}],
                [{"type": "file", "name": "test_4.py"}],
            ],
            "testRunner": "file",
            "rest": [],
            "subsettingId": 123,
            "summary": {
                "subset": {"duration": 10, "candidates": 3, "rate": 50},
                "rest": {"duration": 10, "candidates": 3, "rate": 50}
            },
            "isObservation": True,
        }
        responses.replace(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(
            get_base_url(),
            self.organization,
            self.workspace),
            json=mock_json_response,
            status=200)

        rest = tempfile.NamedTemporaryFile(delete=False)
        result = self.cli("subset", "--target", "30%", "--session",
                          self.session, "--rest", rest.name, "--observation", "file", mix_stderr=False, input=pipe)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, "test_1.py\ntest_2.py\ntest_3.py\ntest_4.py\n")
        self.assertEqual(rest.read().decode(), "")
        rest.close()
        os.unlink(rest.name)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_targetless(self):
        pipe = "test_aaa.py\ntest_bbb.py\ntest_ccc.py\ntest_eee.py\ntest_fff.py\ntest_ggg.py"
        responses.replace(
            responses.POST,
            "{}/intake/organizations/{}/workspaces/{}/subset".format(
                get_base_url(),
                self.organization,
                self.workspace),
            json={
                "testPaths": [
                    [{"type": "file", "name": "test_aaa.py"}],
                    [{"type": "file", "name": "test_bbb.py"}],
                    [{"type": "file", "name": "test_ccc.py"}],
                ],
                "testRunner": "file",
                "rest": [
                    [{"type": "file", "name": "test_eee.py"}],
                    [{"type": "file", "name": "test_fff.py"}],
                    [{"type": "file", "name": "test_ggg.py"}],
                ],
                "subsettingId": 123,
                "summary": {
                    "subset": {"duration": 10, "candidates": 3, "rate": 50},
                    "rest": {"duration": 10, "candidates": 3, "rate": 50}
                },
            },
            status=200)

        result = self.cli(
            "subset",
            "--session",
            self.session,
            "file",
            input=pipe,
            mix_stderr=False)
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(responses.calls[0].request.body).decode())
        self.assertTrue(payload.get('useServerSideOptimizationTarget'))

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_ignore_flaky_tests_above(self):
        pipe = "test_aaa.py\ntest_bbb.py\ntest_ccc.py\ntest_flaky.py"
        responses.replace(
            responses.POST,
            "{}/intake/organizations/{}/workspaces/{}/subset".format(
                get_base_url(),
                self.organization,
                self.workspace),
            json={
                "testPaths": [
                    [{"type": "file", "name": "test_aaa.py"}],
                    [{"type": "file", "name": "test_bbb.py"}],

                ],
                "testRunner": "file",
                "rest": [
                    [{"type": "file", "name": "test_ccc.py"}],
                ],
                "subsettingId": 123,
                "summary": {
                    "subset": {"duration": 20, "candidates": 2, "rate": 67},
                    "rest": {"duration": 10, "candidates": 1, "rate": 33}
                },
            },
            status=200)

        result = self.cli(
            "subset",
            "--session",
            self.session,
            "--ignore-flaky-tests-above",
            0.05,
            "file",
            input=pipe,
            mix_stderr=False)
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(responses.calls[0].request.body).decode())
        self.assertEqual(payload.get('dropFlakinessThreshold'), 0.05)

    @ responses.activate
    @ mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_with_get_tests_from_previous_full_runs(self):
        # check error when input candidates are empty without --get-tests-from-previous-sessions option
        result = self.cli("subset", "--target", "30%", "--session", self.session, "file")
        self.assertEqual(result.exit_code, 1)
        self.assertTrue("Please set subset candidates or use `--get-tests-from-previous-sessions` option" in result.stdout)

        responses.replace(
            responses.POST,
            "{}/intake/organizations/{}/workspaces/{}/subset".format(
                get_base_url(),
                self.organization,
                self.workspace),
            json={
                "testPaths": [
                    [{"type": "file", "name": "test_aaa.py"}],
                    [{"type": "file", "name": "test_bbb.py"}],
                    [{"type": "file", "name": "test_ccc.py"}],
                ],
                "testRunner": "file",
                "rest": [
                    [{"type": "file", "name": "test_eee.py"}],
                    [{"type": "file", "name": "test_fff.py"}],
                    [{"type": "file", "name": "test_ggg.py"}],
                ],
                "subsettingId": 123,
                "summary": {
                    "subset": {"duration": 10, "candidates": 3, "rate": 50},
                    "rest": {"duration": 10, "candidates": 3, "rate": 50}
                },
            },
            status=200)

        rest = tempfile.NamedTemporaryFile(delete=False)
        result = self.cli(
            "subset",
            "--target",
            "30%",
            "--session",
            self.session,
            "--rest",
            rest.name,
            "--get-tests-from-previous-sessions",
            "file",
            mix_stderr=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, "test_aaa.py\ntest_bbb.py\ntest_ccc.py\n")
        self.assertEqual(rest.read().decode(), os.linesep.join(["test_eee.py", "test_fff.py", "test_ggg.py"]))
        rest.close()
        os.unlink(rest.name)

    @ responses.activate
    @ mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_with_output_exclusion_rules(self):
        pipe = "test_aaa.py\ntest_111.py\ntest_bbb.py\ntest_222.py\ntest_ccc.py\ntest_333.py\n"
        responses.replace(
            responses.POST,
            "{}/intake/organizations/{}/workspaces/{}/subset".format(
                get_base_url(),
                self.organization,
                self.workspace),
            json={
                "testPaths": [
                    [{"type": "file", "name": "test_aaa.py"}],
                    [{"type": "file", "name": "test_bbb.py"}],
                    [{"type": "file", "name": "test_ccc.py"}],
                ],
                "testRunner": "file",
                "rest": [
                    [{"type": "file", "name": "test_111.py"}],
                    [{"type": "file", "name": "test_222.py"}],
                    [{"type": "file", "name": "test_333.py"}],
                ],
                "subsettingId": 123,
                "summary": {
                    "subset": {"duration": 15, "candidates": 3, "rate": 70},
                    "rest": {"duration": 6, "candidates": 3, "rate": 30}
                },
            }, status=200)

        rest = tempfile.NamedTemporaryFile(delete=False)
        result = self.cli(
            "subset",
            "--target",
            "70%",
            "--session",
            self.session,
            "--rest",
            rest.name,
            "file",
            input=pipe,
            mix_stderr=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, "test_aaa.py\ntest_bbb.py\ntest_ccc.py\n")
        self.assertEqual(rest.read().decode(), os.linesep.join(["test_111.py", "test_222.py", "test_333.py"]))
        rest.close()
        os.unlink(rest.name)

        rest = tempfile.NamedTemporaryFile(delete=False)
        result = self.cli(
            "subset",
            "--target",
            "70%",
            "--session",
            self.session,
            "--rest",
            rest.name,
            "--output-exclusion-rules",
            "file",
            input=pipe,
            mix_stderr=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, "test_111.py\ntest_222.py\ntest_333.py\n")

        self.assertEqual(rest.read().decode(), os.linesep.join(["test_aaa.py", "test_bbb.py", "test_ccc.py"]))
        rest.close()
        os.unlink(rest.name)

        # case: reset is empty
        responses.replace(
            responses.POST,
            "{}/intake/organizations/{}/workspaces/{}/subset".format(
                get_base_url(),
                self.organization,
                self.workspace),
            json={
                "testPaths": [
                    [{"type": "file", "name": "test_aaa.py"}],
                    [{"type": "file", "name": "test_bbb.py"}],
                    [{"type": "file", "name": "test_ccc.py"}],
                    [{"type": "file", "name": "test_111.py"}],
                    [{"type": "file", "name": "test_222.py"}],
                    [{"type": "file", "name": "test_333.py"}],
                ],
                "testRunner": "file",
                "rest": [],
                "subsettingId": 123,
                "summary": {
                    "subset": {"duration": 15, "candidates": 6, "rate": 100},
                    "rest": {"duration": 0, "candidates": 0, "rate": 0}
                },
            }, status=200)

        rest = tempfile.NamedTemporaryFile(delete=False)
        result = self.cli(
            "subset",
            "--target",
            "70%",
            "--session",
            self.session,
            "--rest",
            rest.name,
            "--output-exclusion-rules",
            "file",
            input=pipe,
            mix_stderr=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, "")

        self.assertEqual(rest.read().decode(), os.linesep.join(
            ["test_aaa.py", "test_bbb.py", "test_ccc.py", "test_111.py", "test_222.py", "test_333.py"]))
        rest.close()
        os.unlink(rest.name)

    @ responses.activate
    @ mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_with_observation_and_output_exclusion_rules(self):
        pipe = "test_aaa.py\ntest_111.py\ntest_bbb.py\ntest_222.py\ntest_ccc.py\ntest_333.py\n"
        responses.replace(
            responses.POST,
            "{}/intake/organizations/{}/workspaces/{}/subset".format(
                get_base_url(),
                self.organization,
                self.workspace),
            json={
                "testPaths": [
                    [{"type": "file", "name": "test_aaa.py"}],
                    [{"type": "file", "name": "test_bbb.py"}],
                    [{"type": "file", "name": "test_ccc.py"}],
                ],
                "testRunner": "file",
                "rest": [
                    [{"type": "file", "name": "test_111.py"}],
                    [{"type": "file", "name": "test_222.py"}],
                    [{"type": "file", "name": "test_333.py"}],
                ],
                "subsettingId": 123,
                "summary": {
                    "subset": {"duration": 15, "candidates": 3, "rate": 70},
                    "rest": {"duration": 6, "candidates": 3, "rate": 30}
                },
                "isObservation": True,
            }, status=200)

        rest = tempfile.NamedTemporaryFile(delete=False)
        result = self.cli(
            "subset",
            "--target",
            "70%",
            "--session",
            self.session,
            "--rest",
            rest.name,
            "--output-exclusion-rules",
            "--observation",
            "file",
            input=pipe,
            mix_stderr=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, "")

        self.assertEqual(rest.read().decode(), os.linesep.join(
            ["test_aaa.py", "test_bbb.py", "test_ccc.py", "test_111.py", "test_222.py", "test_333.py"]))
        rest.close()
        os.unlink(rest.name)
