import os
from pathlib import Path
from unittest import mock

from .cli_test_case import CliTestCase


class PluginTest(CliTestCase):
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_plugin_loading(self):
        """
        Load plugins/foo.py as a plugin and execute its code
        """
        plugin_dir = Path(__file__).parent.joinpath('plugins').resolve()
        result = self.cli('--plugins', str(plugin_dir), 'record', 'tests',
                          '--session', 'builds/dummy/test_sessions/123', 'foo', 'alpha', 'bravo', 'charlie')
        self.assertTrue("foo:alpha" in result.stdout, result.stdout)
        self.assertTrue("foo:bravo" in result.stdout, result.stdout)
        self.assertTrue("foo:charlie" in result.stdout, result.stdout)
