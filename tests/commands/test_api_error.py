import os
import tempfile
from unittest import mock
from pathlib import Path
import responses
from launchable.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class APIErrorTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath(
        '../data/minitest/').resolve()

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_build(self):
        responses.add(responses.POST, "{base}/intake/organizations/{org}/workspaces/{ws}/builds".format(
            base=get_base_url(), org=self.organization, ws=self.workspace), status=500)

        result = self.cli("record", "build", "--name", "example")
        self.assertEqual(result.exit_code, 0)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_session(self):
        build = "internal_server_error"
        responses.add(responses.POST, "{base}/intake/organizations/{org}/workspaces/{ws}/builds/{build}/test_sessions".format(
            base=get_base_url(), org=self.organization, ws=self.workspace, build=build), status=500)

        result = self.cli("record", "session", "--build", build)
        self.assertEqual(result.exit_code, 0)

        build = "not_found"
        responses.add(responses.POST, "{base}/intake/organizations/{org}/workspaces/{ws}/builds/{build}/test_sessions".format(
            base=get_base_url(), org=self.organization, ws=self.workspace, build=build), status=404)

        result = self.cli("record", "session", "--build", build)
        self.assertEqual(result.exit_code, 1)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
        responses.replace(responses.POST, "{base}/intake/organizations/{org}/workspaces/{ws}/subset".format(
            base=get_base_url(), org=self.organization, ws=self.workspace), status=500)

        subset_file = "example_test.rb"

        with tempfile.NamedTemporaryFile(delete=False) as rest_file:
            result = self.cli("subset", "--target", "30%", "--session", self.session, "--rest", rest_file.name,
                              "minitest", str(self.test_files_dir) + "/test/**/*.rb", mix_stderr=False)

            self.assertEqual(result.exit_code, 0)
            self.assertEqual(len(result.stdout.rstrip().split("\n")), 1)
            self.assertTrue(subset_file in result.stdout)

            rest = Path(rest_file.name).read_text()
            self.assertEqual(
                len(rest.rstrip().split("\n")), 1)
            self.assertTrue(subset_file in rest)

        responses.replace(responses.POST, "{base}/intake/organizations/{org}/workspaces/{ws}/subset".format(
            base=get_base_url(), org=self.organization, ws=self.workspace), status=404)

        with tempfile.NamedTemporaryFile(delete=False) as rest_file:
            result = self.cli("subset", "--target", "30%", "--session", self.session, "--rest", rest_file.name,
                              "minitest", str(self.test_files_dir) + "/test/**/*.rb", mix_stderr=False)
            self.assertEqual(result.exit_code, 0)

            self.assertEqual(len(result.stdout.rstrip().split("\n")), 1)
            self.assertTrue(subset_file in result.stdout)

            rest = Path(rest_file.name).read_text()
            self.assertEqual(
                len(rest.rstrip().split("\n")), 1)
            self.assertTrue(subset_file in rest)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_tests(self):
        test_files_dir = Path(__file__).parent.joinpath(
            '../data/minitest/').resolve()

        responses.replace(responses.POST, "{base}/intake/organizations/{org}/workspaces/{ws}/builds/{build}/test_sessions/{session_id}/events".format(
            base=get_base_url(),
            org=self.organization,
            ws=self.workspace,
            build=self.build_name,
            session_id=self.session_id),
            json=[], status=500)

        result = self.cli("record", "tests", "--session", self.session,
                          "minitest", str(test_files_dir) + "/")
        self.assertEqual(result.exit_code, 0)

        responses.replace(responses.POST, "{base}/intake/organizations/{org}/workspaces/{ws}/builds/{build}/test_sessions/{session_id}/events".format(
            base=get_base_url(),
            org=self.organization,
            ws=self.workspace,
            build=self.build_name,
            session_id=self.session_id),
            json=[], status=404)

        result = self.cli("record", "tests", "--session", self.session,
                          "minitest", str(test_files_dir) + "/")
        self.assertEqual(result.exit_code, 0)
