from click.testing import CliRunner
from launchable.__main__ import main
from launchable.version import __version__
from unittest import TestCase


class VersionTest(TestCase):
    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(main, ['--version'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'launchable-cli, version {}\n'.format(__version__))
