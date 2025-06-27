from unittest import TestCase

from typer.testing import CliRunner  # type: ignore

from launchable.__main__ import main
from launchable.version import __version__


class VersionTest(TestCase):
    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(main, ['--version'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(__version__, result.stdout)
