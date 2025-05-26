import json
import os
from unittest import mock

import responses  # type: ignore

from launchable.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class SessionTest(CliTestCase):
    """
    This test needs to specify `clear=True` in mocking because the test is run on GithubActions.
    Otherwise GithubActions will export $GITHUB_* variables at runs.
    """

    @responses.activate
    @mock.patch.dict(os.environ, {
        "LAUNCHABLE_TOKEN": CliTestCase.launchable_token,
        # LANG=C.UTF-8 is needed to run CliRunner().invoke(command).
        # Generally it's provided by shell. But in this case, `clear=True`
        # removes the variable.
        'LANG': 'C.UTF-8',
    }, clear=True)
    def test_run_session_without_flavor(self):
        result = self.cli("record", "session", "--build", self.build_name)
        self.assert_success(result)

        payload = json.loads(responses.calls[0].request.body.decode())
        self.assert_json_orderless_equal({
            "flavors": {},
            "isObservation": False,
            "links": [],
            "noBuild": False,
            "lineage": None,
            "testSuite": None,
            "timestamp": None,
        }, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {
        "LAUNCHABLE_TOKEN": CliTestCase.launchable_token,
        'LANG': 'C.UTF-8',
    }, clear=True)
    def test_run_session_with_flavor(self):
        result = self.cli("record", "session", "--build", self.build_name,
                          "--flavor", "key=value", "--flavor", "k:v", "--flavor", "k e y = v a l u e")
        self.assert_success(result)

        payload = json.loads(responses.calls[0].request.body.decode())
        self.assert_json_orderless_equal({
            "flavors": {
                "key": "value",
                "k": "v",
                "k e y": "v a l u e",
            },
            "isObservation": False,
            "links": [],
            "noBuild": False,
            "lineage": None,
            "testSuite": None,
            "timestamp": None,
        }, payload)

        result = self.cli("record", "session", "--build", self.build_name, "--flavor", "only-key")
        self.assert_exit_code(result, 2)
        self.assertIn("Expected a key-value pair formatted as --option key=value", result.output)

    @responses.activate
    @mock.patch.dict(os.environ, {
        "LAUNCHABLE_TOKEN": CliTestCase.launchable_token,
        'LANG': 'C.UTF-8',
    }, clear=True)
    def test_run_session_with_observation(self):
        result = self.cli("record", "session", "--build", self.build_name, "--observation")
        self.assert_success(result)

        payload = json.loads(responses.calls[0].request.body.decode())

        self.assert_json_orderless_equal({
            "flavors": {},
            "isObservation": True,
            "links": [],
            "noBuild": False,
            "lineage": None,
            "testSuite": None,
            "timestamp": None,
        }, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {
        "LAUNCHABLE_TOKEN": CliTestCase.launchable_token,
        'LANG': 'C.UTF-8',
    }, clear=True)
    def test_run_session_with_session_name(self):
        # session name is already exist
        result = self.cli("record", "session", "--build", self.build_name, "--session-name", self.session_name)
        self.assert_exit_code(result, 2)

        responses.replace(
            responses.GET,
            "{}/intake/organizations/{}/workspaces/{}/builds/{}/test_session_names/{}".format(
                get_base_url(),
                self.organization,
                self.workspace,
                self.build_name,
                self.session_name,
            ),
            status=404,
        )
        # invalid session name
        result = self.cli("record", "session", "--build", self.build_name, "--session-name", "invalid/name")
        self.assert_exit_code(result, 2)

        result = self.cli("record", "session", "--build", self.build_name, "--session-name", self.session_name)
        self.assert_success(result)

        payload = json.loads(responses.calls[3].request.body.decode())
        self.assert_json_orderless_equal({
            "flavors": {},
            "isObservation": False,
            "links": [],
            "noBuild": False,
            "lineage": None,
            "testSuite": None,
            "timestamp": None,
        }, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {
        "LAUNCHABLE_TOKEN": CliTestCase.launchable_token,
        'LANG': 'C.UTF-8',
    }, clear=True)
    def test_run_session_with_lineage(self):
        result = self.cli("record", "session", "--build", self.build_name,
                          "--lineage", "example-lineage")
        self.assert_success(result)

        payload = json.loads(responses.calls[0].request.body.decode())
        self.assert_json_orderless_equal({
            "flavors": {},
            "isObservation": False,
            "links": [],
            "noBuild": False,
            "lineage": "example-lineage",
            "testSuite": None,
            "timestamp": None,
        }, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {
        "LAUNCHABLE_TOKEN": CliTestCase.launchable_token,
        'LANG': 'C.UTF-8',
    }, clear=True)
    def test_run_session_with_test_suite(self):
        result = self.cli("record", "session", "--build", self.build_name,
                          "--test-suite", "example-test-suite")
        self.assert_success(result)

        payload = json.loads(responses.calls[0].request.body.decode())
        self.assert_json_orderless_equal({
            "flavors": {},
            "isObservation": False,
            "links": [],
            "noBuild": False,
            "lineage": None,
            "testSuite": "example-test-suite",
            "timestamp": None,
        }, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {
        "LAUNCHABLE_TOKEN": CliTestCase.launchable_token,
        'LANG': 'C.UTF-8',
    }, clear=True)
    def test_run_session_with_timestamp(self):
        result = self.cli("record", "session", "--build", self.build_name,
                          "--timestamp", "2023-10-01T12:00:00Z")
        self.assert_success(result)

        payload = json.loads(responses.calls[0].request.body.decode())
        self.assert_json_orderless_equal({
            "flavors": {},
            "isObservation": False,
            "links": [],
            "noBuild": False,
            "lineage": None,
            "testSuite": None,
            "timestamp": "2023-10-01T12:00:00+00:00",
        }, payload)
