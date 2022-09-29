from launchable.commands.record.session import CIRCLECI_BUILD_URL_KEY, CIRCLECI_KEY, GITHUB_ACTIONS_KEY, GITHUB_ACTIONS_REPOSITORY_KEY, GITHUB_ACTIONS_RUN_ID_KEY, GITHUB_ACTIONS_SERVER_URL_KEY, JENKINS_BUILD_URL_KEY, JENKINS_URL_KEY
from tests.cli_test_case import CliTestCase
import responses  # type: ignore
import json
import os
from unittest import mock


class SessionTest(CliTestCase):
    """
    This test needs to specify `clear=True` in mocking because the test is run on GithubActions. 
    Otherwise GithubActions will export $GITHUB_* variables at runs.
    """

    @responses.activate
    @mock.patch.dict(os.environ, {
        "LAUNCHABLE_TOKEN": CliTestCase.launchable_token,
        # LANG=C.UTF-8 is needed to run CliRunner().invoke(command).
        # Generally it's provided by shell. But in this case, `clear=True` removes the variable.
        'LANG': 'C.UTF-8',
    }, clear=True)
    def test_run_session_without_flavor(self):
        result = self.cli("record", "session", "--build", self.build_name)
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(responses.calls[0].request.body.decode())
        self.assert_json_orderless_equal(
            {"flavors": {}, "isObservation": False}, payload)

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
            "isObservation": False, }, payload)

        with self.assertRaises(ValueError):
            result = self.cli("record", "session", "--build", self.build_name,
                              "--flavor", "only-key")
            self.assertEqual(result.exit_code, 1)
            self.assertTrue(
                "Expected key-value like --option kye=value or --option key value." in result.output)

    @responses.activate
    @mock.patch.dict(os.environ, {
        "LAUNCHABLE_TOKEN": CliTestCase.launchable_token,
        'LANG': 'C.UTF-8',
    }, clear=True)
    def test_run_session_with_observation(self):
        result = self.cli("record", "session", "--build",
                          self.build_name, "--observation")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(responses.calls[0].request.body.decode())
        self.assert_json_orderless_equal(
            {"flavors": {}, "isObservation": True}, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {
        "LAUNCHABLE_TOKEN": CliTestCase.launchable_token,
        JENKINS_URL_KEY: "https://jenkins.example.com/",
        JENKINS_BUILD_URL_KEY: "https://jenkins.example.com/job/launchableinc/job/example/357/",
        'LANG': 'C.UTF-8',
    }, clear=True)
    def test_run_session_with_jenkins_url(self):
        result = self.cli("record", "session", "--build", self.build_name)
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(responses.calls[0].request.body.decode())
        self.assert_json_orderless_equal(
            {
                "flavors": {},
                "isObservation": False,
                "link": {
                    "provider": "jenkins",
                    "url": "https://jenkins.example.com/job/launchableinc/job/example/357/"},
            },
            payload)

    @responses.activate
    @mock.patch.dict(os.environ, {
        "LAUNCHABLE_TOKEN": CliTestCase.launchable_token,
        GITHUB_ACTIONS_KEY: "true",
        GITHUB_ACTIONS_SERVER_URL_KEY: "https://github.com",
        GITHUB_ACTIONS_REPOSITORY_KEY: "launchableinc/example",
        GITHUB_ACTIONS_RUN_ID_KEY: "2709244304",
        'LANG': 'C.UTF-8',
    }, clear=True)
    def test_run_session_with_github_url(self):
        result = self.cli("record", "session", "--build", self.build_name)
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(responses.calls[0].request.body.decode())
        self.assert_json_orderless_equal(
            {
                "flavors": {},
                "isObservation": False,
                "link": {
                    "provider": "github-actions",
                    "url": "https://github.com/launchableinc/example/actions/runs/2709244304",
                },
            }, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {
        "LAUNCHABLE_TOKEN": CliTestCase.launchable_token,
        CIRCLECI_KEY: "true",
        CIRCLECI_BUILD_URL_KEY: "https://app.circleci.com/pipelines/github/launchableinc/examples/6221/workflows/990a9987-1a21-42e5-a332-89046125e5ce/jobs/7935",
        'LANG': 'C.UTF-8',
    }, clear=True)
    def test_run_session_with_circleci_url(self):
        result = self.cli("record", "session", "--build", self.build_name)
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(responses.calls[0].request.body.decode())
        self.assert_json_orderless_equal(
            {
                "flavors": {},
                "isObservation": False,
                "link": {
                    "provider": "circleci",
                    "url": "https://app.circleci.com/pipelines/github/launchableinc/examples/6221/workflows/990a9987-1a21-42e5-a332-89046125e5ce/jobs/7935",
                },
            }, payload)
