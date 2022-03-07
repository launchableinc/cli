from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import threading
from typing import Any
from unittest import mock
from tests.cli_test_case import CliTestCase
from launchable.utils.env_keys import BASE_URL_KEY
from launchable.commands.record.commit import _build_proxy_option
from tests.helper import ignore_warnings


class CommitHandler(SimpleHTTPRequestHandler):
    # mock commits/latest
    def do_GET(self):
        response = []
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode("utf-8"))

    # mock commits/collect
    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()


class CommitTest(CliTestCase):
    @ mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_run_commit(self):
        server = HTTPServer(("", 0), CommitHandler)
        thread = threading.Thread(None, server.serve_forever)
        thread.start()

        host, port = server.server_address
        endpoint = "http://{}:{}".format(host, port)

        with mock.patch.dict(os.environ, {BASE_URL_KEY: endpoint}):
            result = self.cli("record", "commit")
            self.assertEqual(result.exit_code, 0, "exit normally")

        server.shutdown()
        thread.join()

    def test_proxy_options(self):
        self.assertEqual(_build_proxy_option("https://some_proxy:1234"),
                         "-Dhttps.proxyHost=some_proxy -Dhttps.proxyPort=1234 ")
        self.assertEqual(_build_proxy_option("some_proxy:1234"),
                         "-Dhttps.proxyHost=some_proxy -Dhttps.proxyPort=1234 ")
        self.assertEqual(_build_proxy_option("some_proxy"),
                         "-Dhttps.proxyHost=some_proxy ")
        self.assertEqual(_build_proxy_option(
            "https://some_proxy"), "-Dhttps.proxyHost=some_proxy ")
        self.assertEqual(_build_proxy_option("http://yoyoyo"),
                         "-Dhttps.proxyHost=yoyoyo ")
