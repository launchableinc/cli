from tests.cli_test_case import CliTestCase
import responses  # type: ignore
import json
import os
from unittest import mock


class SessionTest(CliTestCase):

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_run_session_without_flavor(self):
        result = self.cli("record", "session", "--build", self.build_name)
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(responses.calls[0].request.body.decode())
        self.assert_json_orderless_equal(
            {"flavors": {}, "observation": False}, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
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
            "observation": False, }, payload)

        with self.assertRaises(ValueError):
            result = self.cli("record", "session", "--build", self.build_name,
                              "--flavor", "only-key")
            self.assertEqual(result.exit_code, 1)
            self.assertTrue(
                "Expected key-value like --option kye=value or --option key value." in result.output)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_run_session_with_observation(self):
        result = self.cli("record", "session", "--build",
                          self.build_name, "--observation")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(responses.calls[0].request.body.decode())
        self.assert_json_orderless_equal(
            {"flavors": {}, "observation": True}, payload)
