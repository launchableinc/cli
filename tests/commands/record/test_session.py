from tests.cli_test_case import CliTestCase
import responses  # type: ignore
import json


class SessionTest(CliTestCase):

    @responses.activate
    def test_run_session_without_flavor(self):
        result = self.cli("record", "session", "--build", self.build_name)
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(responses.calls[0].request.body)
        self.assert_json_orderless_equal({"flavors": {}}, payload)

    @responses.activate
    def test_run_session_with_flavor(self):
        result = self.cli("record", "session", "--build", self.build_name,
                          "--flavor", "key", "value", "--flavor", "k", "v")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(responses.calls[0].request.body)
        self.assert_json_orderless_equal({"flavors": {
            "key": "value",
            "k": "v",
        }}, payload)
