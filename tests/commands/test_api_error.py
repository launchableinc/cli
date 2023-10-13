import json
import os
import platform
import tempfile
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from unittest import mock

import responses  # type: ignore
from requests.exceptions import ReadTimeout

from launchable.commands.verify import compare_version
from launchable.utils.env_keys import BASE_URL_KEY
from launchable.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


# dummy server for exe.jar
# exe.jar calls commits/latest (GET) then commits/collect (POST)
class SuccessCommitHandlerMock(SimpleHTTPRequestHandler):
    def do_GET(self):
        body = []
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode("utf-8"))

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()


class ErrorCommitHandlerMock(SimpleHTTPRequestHandler):
    def do_GET(self):
        body = []
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode("utf-8"))

    def do_POST(self):
        body = {"reason": "Internal server error"}
        self.send_response(500)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode("utf-8"))


CLI_TRACKING_URL = "{base}/intake/cli_tracking"


class APIErrorTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath('../data/minitest/').resolve()

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_verify(self):
        verification_url = "{base}/intake/organizations/{org}/workspaces/{ws}/verification".format(
            base=get_base_url(),
            org=self.organization,
            ws=self.workspace)
        responses.add(
            responses.GET,
            verification_url,
            body=ReadTimeout("error"))
        result = self.cli("verify")
        self.assertEqual(result.exit_code, 0)

        responses.add(
            responses.GET,
            verification_url,
            body=ConnectionError("error"))
        tracking = responses.add(
            responses.POST,
            CLI_TRACKING_URL.format(
                base=get_base_url()),
            body=ReadTimeout("error"))
        result = self.cli("verify")
        self.assertEqual(result.exit_code, 0)
        # Since Timeout error is caught inside of LaunchableClient, the tracking event is sent twice.
        self.assert_tracking_count(tracking=tracking, count=2)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_commit(self):
        server = HTTPServer(("", 0), ErrorCommitHandlerMock)
        thread = threading.Thread(None, server.serve_forever)
        thread.start()

        host, port = server.server_address
        endpoint = "http://{}:{}".format(host, port)

        with mock.patch.dict(os.environ, {BASE_URL_KEY: endpoint}):
            result = self.cli("record", "commit", "--source", ".")
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.exception, None)

        server.shutdown()
        thread.join()

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_build(self):
        # case: cli catches error
        success_server = HTTPServer(("", 0), SuccessCommitHandlerMock)
        thread = threading.Thread(None, success_server.serve_forever)
        thread.start()

        host, port = success_server.server_address
        endpoint = "http://{}:{}".format(host, port)
        with mock.patch.dict(os.environ, {BASE_URL_KEY: endpoint}):
            responses.add(responses.POST, "{base}/intake/organizations/{org}/workspaces/{ws}/builds".format(
                base=get_base_url(), org=self.organization, ws=self.workspace), status=500)
            tracking = responses.add(
                responses.POST,
                CLI_TRACKING_URL.format(
                    base=get_base_url()),
                body=ReadTimeout("error"))

            result = self.cli("record", "build", "--name", "example")
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.exception, None)
            # Since HTTPError is occurred outside of LaunchableClient, the count is 1.
            self.assert_tracking_count(tracking=tracking, count=1)

        success_server.shutdown()
        thread.join()

        # case: exe.jar catches error
        error_server = HTTPServer(("", 0), ErrorCommitHandlerMock)
        thread = threading.Thread(None, error_server.serve_forever)
        thread.start()

        host, port = error_server.server_address
        endpoint = "http://{}:{}".format(host, port)

        with mock.patch.dict(os.environ, {BASE_URL_KEY: endpoint}):
            responses.add(responses.POST, "{base}/intake/organizations/{org}/workspaces/{ws}/builds".format(
                base=get_base_url(), org=self.organization, ws=self.workspace), status=500)
            tracking = responses.add(
                responses.POST,
                CLI_TRACKING_URL.format(
                    base=get_base_url()),
                body=ReadTimeout("error"))

            result = self.cli("record", "build", "--name", "example")
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.exception, None)
            # Since HTTPError is occurred outside of LaunchableClient, the count is 1.
            self.assert_tracking_count(tracking=tracking, count=1)

        error_server.shutdown()
        thread.join()

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_session(self):
        build = "internal_server_error"
        responses.add(
            responses.POST,
            "{base}/intake/organizations/{org}/workspaces/{ws}/builds/{build}/test_sessions".format(
                base=get_base_url(),
                org=self.organization,
                ws=self.workspace,
                build=build),
            status=500)
        tracking = responses.add(
            responses.POST,
            CLI_TRACKING_URL.format(
                base=get_base_url()),
            body=ReadTimeout("error"))

        result = self.cli("record", "session", "--build", build)
        self.assertEqual(result.exit_code, 0)
        # Since HTTPError is occurred outside of LaunchableClient, the count is 1.
        self.assert_tracking_count(tracking=tracking, count=1)

        build = "not_found"
        responses.add(
            responses.POST,
            "{base}/intake/organizations/{org}/workspaces/{ws}/builds/{build}/test_sessions".format(
                base=get_base_url(),
                org=self.organization,
                ws=self.workspace,
                build=build),
            status=404)
        tracking = responses.add(
            responses.POST,
            CLI_TRACKING_URL.format(
                base=get_base_url()),
            body=ReadTimeout("error"))

        result = self.cli("record", "session", "--build", build)
        self.assertEqual(result.exit_code, 1)
        self.assert_tracking_count(tracking=tracking, count=1)

        responses.replace(
            responses.GET,
            "{}/intake/organizations/{}/workspaces/{}/builds/{}/test_session_names/{}".format(
                get_base_url(),
                self.organization,
                self.workspace,
                self.build_name,
                self.session_name,
            ),
            body=ReadTimeout("error")
        )
        tracking = responses.add(
            responses.POST,
            CLI_TRACKING_URL.format(
                base=get_base_url()),
            body=ReadTimeout("error"))

        result = self.cli("record", "session", "--build", self.build_name, "--session-name", self.session_name)
        self.assertEqual(result.exit_code, 0)
        # Since Timeout error is caught inside of LaunchableClient, the tracking event is sent twice.
        self.assert_tracking_count(tracking=tracking, count=2)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
        responses.replace(
            responses.POST,
            "{base}/intake/organizations/{org}/workspaces/{ws}/subset".format(
                base=get_base_url(),
                org=self.organization,
                ws=self.workspace),
            status=500)
        tracking = responses.add(
            responses.POST,
            CLI_TRACKING_URL.format(
                base=get_base_url()),
            body=ReadTimeout("error"))

        subset_file = "example_test.rb"

        with tempfile.NamedTemporaryFile(delete=False) as rest_file:
            result = self.cli(
                "subset",
                "--target",
                "30%",
                "--session",
                self.session,
                "--rest",
                rest_file.name,
                "minitest",
                str(self.test_files_dir) + "/test/**/*.rb",
                mix_stderr=False)

            self.assertEqual(result.exit_code, 0)
            self.assertEqual(len(result.stdout.rstrip().split("\n")), 1)
            self.assertTrue(subset_file in result.stdout)
            self.assertEqual(Path(rest_file.name).read_text(), "")
            # Since HTTPError is occurred outside of LaunchableClient, the count is 1.
            self.assert_tracking_count(tracking=tracking, count=1)

        responses.replace(responses.POST, "{base}/intake/organizations/{org}/workspaces/{ws}/subset".format(
            base=get_base_url(), org=self.organization, ws=self.workspace), status=404)

        with tempfile.NamedTemporaryFile(delete=False) as rest_file:
            result = self.cli("subset", "--target", "30%", "--session", self.session, "--rest", rest_file.name,
                              "minitest", str(self.test_files_dir) + "/test/**/*.rb", mix_stderr=False)
            self.assertEqual(result.exit_code, 0)

            self.assertEqual(len(result.stdout.rstrip().split("\n")), 1)
            self.assertTrue(subset_file in result.stdout)
            self.assertEqual(Path(rest_file.name).read_text(), "")

        responses.replace(
            responses.GET,
            "{base}/intake/organizations/{org}/workspaces/{ws}/builds/{build}/test_sessions/{session_id}".format(
                base=get_base_url(),
                org=self.organization,
                ws=self.workspace,
                build=self.build_name,
                session_id=self.session_id),
            body=ReadTimeout("error"))
        tracking = responses.add(
            responses.POST,
            CLI_TRACKING_URL.format(
                base=get_base_url()),
            body=ReadTimeout("error"))
        with tempfile.NamedTemporaryFile(delete=False) as rest_file:
            result = self.cli("subset",
                              "--target",
                              "30%",
                              "--session",
                              self.session,
                              "--rest",
                              rest_file.name,
                              "--observation",
                              "minitest",
                              str(self.test_files_dir) + "/test/**/*.rb", mix_stderr=False)
            self.assertEqual(result.exit_code, 0)
            # Since Timeout error is caught inside of LaunchableClient, the tracking event is sent twice.
            self.assert_tracking_count(tracking=tracking, count=2)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_tests(self):
        responses.replace(
            responses.POST,
            "{base}/intake/organizations/{org}/workspaces/{ws}/builds/{build}/test_sessions/{session_id}/events".format(
                base=get_base_url(),
                org=self.organization,
                ws=self.workspace,
                build=self.build_name,
                session_id=self.session_id),
            json=[], status=500)
        tracking = responses.add(
            responses.POST,
            CLI_TRACKING_URL.format(
                base=get_base_url()),
            body=ReadTimeout("error"))

        result = self.cli("record", "tests", "--session", self.session, "minitest", str(self.test_files_dir) + "/")
        self.assertEqual(result.exit_code, 0)
        # Since HTTPError is occurred outside of LaunchableClient, the count is 1.
        self.assert_tracking_count(tracking=tracking, count=1)

        responses.replace(
            responses.POST,
            "{base}/intake/organizations/{org}/workspaces/{ws}/builds/{build}/test_sessions/{session_id}/events".format(
                base=get_base_url(),
                org=self.organization,
                ws=self.workspace,
                build=self.build_name,
                session_id=self.session_id),
            json=[], status=404)
        tracking = responses.add(
            responses.POST,
            CLI_TRACKING_URL.format(
                base=get_base_url()),
            body=ReadTimeout("error"))

        result = self.cli("record", "tests", "--session", self.session, "minitest", str(self.test_files_dir) + "/")
        self.assertEqual(result.exit_code, 0)

        self.assert_tracking_count(tracking=tracking, count=1)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_all_workflow_when_server_down(self):
        # setup verify
        responses.add(
            responses.GET,
            "{base}/intake/organizations/{org}/workspaces/{ws}/verification".format(
                base=get_base_url(),
                org=self.organization,
                ws=self.workspace),
            body=ReadTimeout("error"))
        tracking = responses.add(
            responses.POST,
            CLI_TRACKING_URL.format(
                base=get_base_url()),
            body=ReadTimeout("error"))
        # setup build
        responses.replace(
            responses.POST,
            "{base}/intake/organizations/{org}/workspaces/{ws}/builds".format(
                base=get_base_url(),
                org=self.organization,
                ws=self.workspace),
            body=ReadTimeout("error"))
        # setup subset
        responses.replace(
            responses.GET,
            "{base}/intake/organizations/{org}/workspaces/{ws}/builds/{build}/test_sessions/{session_id}".format(
                base=get_base_url(),
                org=self.organization,
                ws=self.workspace,
                build=self.build_name,
                session_id=self.session_id),
            body=ReadTimeout("error"))
        # setup recording tests
        responses.replace(
            responses.POST,
            "{base}/intake/organizations/{org}/workspaces/{ws}/builds/{build}/test_sessions/{session_id}/events".format(
                base=get_base_url(),
                org=self.organization,
                ws=self.workspace,
                build=self.build_name,
                session_id=self.session_id),
            body=ReadTimeout("error"))

        # test commands
        result = self.cli("verify")
        self.assertEqual(result.exit_code, 0)
        # Since Timeout error is caught inside of LaunchableClient, the tracking event is sent twice.
        self.assert_tracking_count(tracking=tracking, count=2)

        result = self.cli("record", "build", "--name", "example")
        self.assert_success(result)

        # Since Timeout error is caught inside of LaunchableClient, the tracking event is sent twice.
        self.assert_tracking_count(tracking=tracking, count=4)

        # set delete=False to solve the error `PermissionError: [Errno 13] Permission denied:` on Windows.
        with tempfile.NamedTemporaryFile(delete=False) as rest_file:
            result = self.cli("subset",
                              "--target",
                              "30%",
                              "--session",
                              self.session,
                              "--rest",
                              rest_file.name,
                              "--observation",
                              "minitest",
                              str(self.test_files_dir) + "/test/**/*.rb", mix_stderr=False)
            self.assertEqual(result.exit_code, 0)

        # Since Timeout error is caught inside of LaunchableClient, the tracking event is sent twice.
        self.assert_tracking_count(tracking=tracking, count=6)

        result = self.cli("record", "tests", "--session", self.session, "minitest", str(self.test_files_dir) + "/")
        self.assertEqual(result.exit_code, 0)
        # Since Timeout error is caught inside of LaunchableClient, the tracking event is sent twice.
        self.assert_tracking_count(tracking=tracking, count=8)

    def assert_tracking_count(self, tracking, count: int):
        # Prior to 3.6, `Response` object can't be obtained.
        if compare_version([int(x) for x in platform.python_version().split('.')], [3, 7]) >= 0:
            assert tracking.call_count == count
