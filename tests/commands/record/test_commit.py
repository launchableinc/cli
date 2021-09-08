import os
from unittest import mock
from tests.cli_test_case import CliTestCase
from launchable.commands.record.commit import _build_proxy_option


class CommitTest(CliTestCase):

    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_run_commit(self):
        """
        `record commit` command cause error because we can't mock Apache HTTP Client in Java
        """
        result = self.cli("record", "commit")
        self.assertEqual(result.exit_code, 0, "exit normally")

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
