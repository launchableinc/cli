import os
from pathlib import Path
from unittest import mock

import responses  # type: ignore

from smart_tests.utils.http_client import get_base_url

from .cli_test_case import CliTestCase


class PluginTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_plugin_loading(self):
        # Manually load the plugin to ensure it's available for the test
        import importlib.util

        plugin_dir = Path(__file__).parent.joinpath('plugins').resolve()
        for f in plugin_dir.glob('*.py'):
            spec = importlib.util.spec_from_file_location(
                f"smart_tests.plugins.{f.stem}", f)
            plugin = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin)
        responses.add(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/{self.workspace}/builds/dummy",
            json={'createdAt': "2020-01-02T03:45:56.123+00:00", 'id': 123, "build": "dummy"},
            status=200)

        # Session existence check
        responses.add(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/{self.workspace}"
            f"/builds/dummy/test_session_names/123",
            json={'id': 123},
            status=200)

        responses.add(
            responses.POST,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/{self.workspace}"
            f"/builds/dummy/test_sessions/{123}/events",
            json={},
            status=200)

        """
        Load plugins/foo.py as a plugin and execute its code
        """
        plugin_dir = Path(__file__).parent.joinpath('plugins').resolve()
        result = self.cli('--plugins', str(plugin_dir), 'record', 'test', 'foo',
                          '--session', '123', '--build', 'dummy', 'alpha', 'bravo', 'charlie')
        self.assertTrue("foo:alpha" in result.stdout, result.stdout)
        self.assertTrue("foo:bravo" in result.stdout, result.stdout)
        self.assertTrue("foo:charlie" in result.stdout, result.stdout)
