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
                          "--flavor", "key=value", "--flavor", "k = v", "--flavor", "k e y = v a l u e", "--flavor", "no-value",)
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(responses.calls[0].request.body)
        self.assert_json_orderless_equal({"flavors": {
            "key": "value",
            "k": "v",
            "k e y": "v a l u e",
        }}, payload)

        self.assertTrue(
            "Skip to set --flavor no-value." in result.output)
