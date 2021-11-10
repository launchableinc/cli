import os

from launchable.utils.session import write_build, write_session
from .cli_test_case import CliTestCase
from pathlib import Path
from unittest import mock


class PluginTest(CliTestCase):
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_plugin_loading(self):
        """
        Load plugins/foo.py as a plugin and execute its code
        """
        # emulate record build
        write_build(self.build_name)

        plugin_dir = Path(__file__).parent.joinpath('plugins').resolve()
        result = self.cli('--plugins', str(plugin_dir), 'record', 'tests',
                          '--session', 'builds/123/test_sessions/16', 'foo', 'alpha', 'bravo', 'charlie')
        self.assertTrue("foo:alpha" in result.stdout, result.stdout)
        self.assertTrue("foo:bravo" in result.stdout, result.stdout)
        self.assertTrue("foo:charlie" in result.stdout, result.stdout)
