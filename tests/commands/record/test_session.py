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
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(responses.calls[0].request.body.decode())
        self.assert_json_orderless_equal({"flavors": {}, "isObservation": False, "links": [], "noBuild": False}, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {
        "LAUNCHABLE_TOKEN": CliTestCase.launchable_token,
        'LANG': 'C.UTF-8',
    }, clear=True)
    def test_run_session_with_flavor(self):
        result = self.cli("record", "session", "--build", self.build_name,
                          "--flavor", "key=value", "--flavor", "k", "v", "--flavor", "k e y = v a l u e")
        self.assertEqual(result.exit_code, 0)

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
        }, payload)

        with self.assertRaises(ValueError):
            result = self.cli("record", "session", "--build", self.build_name, "--flavor", "only-key")
            self.assertEqual(result.exit_code, 1)
            self.assertTrue(
                "Expected key-value like --option kye=value or --option key value." in result.output)

    @responses.activate
    @mock.patch.dict(os.environ, {
        "LAUNCHABLE_TOKEN": CliTestCase.launchable_token,
        'LANG': 'C.UTF-8',
    }, clear=True)
    def test_run_session_with_observation(self):
        result = self.cli("record", "session", "--build", self.build_name, "--observation")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(responses.calls[0].request.body.decode())

        self.assert_json_orderless_equal({"flavors": {}, "isObservation": True, "links": [], "noBuild": False}, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {
        "LAUNCHABLE_TOKEN": CliTestCase.launchable_token,
        'LANG': 'C.UTF-8',
    }, clear=True)
    def test_run_session_with_session_name(self):
        # session name is already exist
        result = self.cli("record", "session", "--build", self.build_name, "--session-name", self.session_name)
        self.assertEqual(result.exit_code, 2)

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
        self.assertEqual(result.exit_code, 2)

        result = self.cli("record", "session", "--build", self.build_name, "--session-name", self.session_name)
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(responses.calls[2].request.body.decode())
        self.assert_json_orderless_equal({"flavors": {}, "isObservation": False, "links": [], "noBuild": False}, payload)
