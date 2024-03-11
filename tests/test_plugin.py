import os
from pathlib import Path
from unittest import mock

import responses  # type: ignore

from launchable.utils.http_client import get_base_url

from .cli_test_case import CliTestCase


class PluginTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_plugin_loading(self):
        responses.add(
            responses.GET,
            "{}/intake/organizations/{}/workspaces/{}/builds/{}".format(
                get_base_url(),
                self.organization,
                self.workspace,
                "dummy"),
            json={'createdAt': "2020-01-02T03:45:56.123+00:00", 'id': 123, "build": "dummy"},
            status=200)

        responses.add(
            responses.POST,
            "{}/intake/organizations/{}/workspaces/{}/builds/{}/test_sessions{}/events".format(
                get_base_url(),
                self.organization,
                self.workspace,
                "dummy", 123),
            json={},
            status=200)

        """
        Load plugins/foo.py as a plugin and execute its code
        """
        plugin_dir = Path(__file__).parent.joinpath('plugins').resolve()
        result = self.cli('--plugins', str(plugin_dir), 'record', 'tests',
                          '--session', 'builds/dummy/test_sessions/123', 'foo', 'alpha', 'bravo', 'charlie')
        self.assertTrue("foo:alpha" in result.stdout, result.stdout)
        self.assertTrue("foo:bravo" in result.stdout, result.stdout)
        self.assertTrue("foo:charlie" in result.stdout, result.stdout)
