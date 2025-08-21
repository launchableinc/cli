import json
import os
from unittest import mock

import responses  # type: ignore

from smart_tests.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class SessionTest(CliTestCase):
    """
    This test needs to specify `clear=True` in mocking because the test is run on GithubActions.
    Otherwise GithubActions will export $GITHUB_* variables at runs.
    """

    @responses.activate
    @mock.patch.dict(os.environ, {
        "SMART_TESTS_TOKEN": CliTestCase.smart_tests_token,
        # LANG=C.UTF-8 is needed to run CliRunner().invoke(command).
        # Generally it's provided by shell. But in this case, `clear=True`
        # removes the variable.
        'LANG': 'C.UTF-8',
    }, clear=True)
    def test_run_session_without_flavor(self):
        # Mock session name check
        responses.add(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/"
            f"{self.workspace}/builds/{self.build_name}/test_session_names/{self.session_name}",
            status=404)

        result = self.cli(
            "record",
            "session",
            "--build",
            self.build_name,
            "--session",
            self.session_name,
            "--test-suite",
            "test-suite")
        self.assert_success(result)

        payload = json.loads(responses.calls[1].request.body.decode())
        self.assert_json_orderless_equal({
            "flavors": {},
            "isObservation": False,
            "links": [],
            "noBuild": False,
            "testSuite": "test-suite",
            "timestamp": None,
        }, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {
        "SMART_TESTS_TOKEN": CliTestCase.smart_tests_token,
        'LANG': 'C.UTF-8',
    }, clear=True)
    def test_run_session_with_flavor(self):
        # Mock session name check
        responses.add(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/"
            f"{self.workspace}/builds/{self.build_name}/test_session_names/{self.session_name}",
            status=404)

        result = self.cli("record", "session", "--build", self.build_name,
                          "--session", self.session_name,
                          "--test-suite", "test-suite",
                          "--flavor", "key=value", "--flavor", "k:v", "--flavor", "k e y = v a l u e")
        self.assert_success(result)

        payload = json.loads(responses.calls[1].request.body.decode())
        self.assert_json_orderless_equal({
            "flavors": {
                "key": "value",
                "k": "v",
                "k e y": "v a l u e",
            },
            "isObservation": False,
            "links": [],
            "noBuild": False,
            "testSuite": "test-suite",
            "timestamp": None,
        }, payload)

        # Mock session name check for second call
        responses.add(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/"
            f"{self.workspace}/builds/{self.build_name}/test_session_names/{self.session_name}",
            status=404)

        result = self.cli(
            "record",
            "session",
            "--build",
            self.build_name,
            "--session",
            self.session_name,
            "--test-suite",
            "test-suite",
            "--flavor",
            "only-key")
        self.assert_exit_code(result, 2)
        self.assertIn("but got 'only-key'", result.output)

    @responses.activate
    @mock.patch.dict(os.environ, {
        "SMART_TESTS_TOKEN": CliTestCase.smart_tests_token,
        'LANG': 'C.UTF-8',
    }, clear=True)
    def test_run_session_with_observation(self):
        # Mock session name check
        responses.add(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/"
            f"{self.workspace}/builds/{self.build_name}/test_session_names/{self.session_name}",
            status=404)

        result = self.cli(
            "record",
            "session",
            "--build",
            self.build_name,
            "--session",
            self.session_name,
            "--test-suite",
            "test-suite",
            "--observation")
        self.assert_success(result)

        payload = json.loads(responses.calls[1].request.body.decode())

        self.assert_json_orderless_equal({
            "flavors": {},
            "isObservation": True,
            "links": [],
            "noBuild": False,
            "testSuite": "test-suite",
            "timestamp": None,
        }, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {
        "SMART_TESTS_TOKEN": CliTestCase.smart_tests_token,
        'LANG': 'C.UTF-8',
    }, clear=True)
    def test_run_session_with_session_name(self):
        # Replace mock for session existence check to return 200 (session exists)
        responses.replace(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/"
            f"{self.workspace}/builds/{self.build_name}/test_session_names/{self.session_name}",
            json={'id': self.session_id},
            status=200)

        # session name is already exist
        result = self.cli(
            "record",
            "session",
            "--build",
            self.build_name,
            "--session",
            self.session_name,
            "--test-suite",
            "test-suite")
        self.assert_exit_code(result, 2)

        responses.replace(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/"
            f"{self.workspace}/builds/{self.build_name}/test_session_names/{self.session_name}",
            status=404,
        )
        # Add mock for invalid session name check
        responses.add(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/"
            f"{self.workspace}/builds/{self.build_name}/test_session_names/invalid/name",
            status=404,
        )
        # invalid session name
        result = self.cli(
            "record",
            "session",
            "--build",
            self.build_name,
            "--session",
            "invalid/name",
            "--test-suite",
            "test-suite")
        self.assert_exit_code(result, 2)

        result = self.cli(
            "record",
            "session",
            "--build",
            self.build_name,
            "--session",
            self.session_name,
            "--test-suite",
            "test-suite")
        self.assert_success(result)

        payload = json.loads(responses.calls[5].request.body.decode())
        self.assert_json_orderless_equal({
            "flavors": {},
            "isObservation": False,
            "links": [],
            "noBuild": False,
            "testSuite": "test-suite",
            "timestamp": None,
        }, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {
        "SMART_TESTS_TOKEN": CliTestCase.smart_tests_token,
        'LANG': 'C.UTF-8',
    }, clear=True)
    def test_run_session_with_lineage(self):
        # Mock session name check
        responses.add(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/"
            f"{self.workspace}/builds/{self.build_name}/test_session_names/test-session",
            status=404)

        result = self.cli("record", "session", "--build", self.build_name,
                          "--session", "test-session", "--test-suite", "test-suite",
                          "--link", "title:example-lineage")
        self.assert_success(result)

        payload = json.loads(responses.calls[1].request.body.decode())
        self.assert_json_orderless_equal({
            "flavors": {},
            "isObservation": False,
            "links": [{"kind": "CUSTOM_LINK", "title": "title", "url": "example-lineage"}],
            "noBuild": False,
            "testSuite": "test-suite",
            "timestamp": None,
        }, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {
        "SMART_TESTS_TOKEN": CliTestCase.smart_tests_token,
        'LANG': 'C.UTF-8',
    }, clear=True)
    def test_run_session_with_test_suite(self):
        # Mock session name check
        responses.add(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/"
            f"{self.workspace}/builds/{self.build_name}/test_session_names/{self.session_name}",
            status=404)

        result = self.cli("record", "session", "--build", self.build_name,
                          "--session", self.session_name,
                          "--test-suite", "example-test-suite")
        self.assert_success(result)

        payload = json.loads(responses.calls[1].request.body.decode())
        self.assert_json_orderless_equal({
            "flavors": {},
            "isObservation": False,
            "links": [],
            "noBuild": False,
            "testSuite": "example-test-suite",
            "timestamp": None,
        }, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {
        "SMART_TESTS_TOKEN": CliTestCase.smart_tests_token,
        'LANG': 'C.UTF-8',
    }, clear=True)
    def test_run_session_with_timestamp(self):
        # Mock session name check
        responses.add(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/"
            f"{self.workspace}/builds/{self.build_name}/test_session_names/{self.session_name}",
            status=404)

        result = self.cli("record", "session", "--build", self.build_name,
                          "--session", self.session_name,
                          "--test-suite", "test-suite",
                          "--timestamp", "2023-10-01T12:00:00Z")
        self.assert_success(result)

        payload = json.loads(responses.calls[1].request.body.decode())
        self.assert_json_orderless_equal({
            "flavors": {},
            "isObservation": False,
            "links": [],
            "noBuild": False,
            "testSuite": "test-suite",
            "timestamp": "2023-10-01T12:00:00+00:00",
        }, payload)
