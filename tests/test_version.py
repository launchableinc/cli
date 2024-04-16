from time import sleep
from unittest import TestCase, TextTestResult

from click.testing import CliRunner  # type: ignore

from launchable.__main__ import main
from launchable.version import __version__


class RetryTestCase(TestCase):
    RETRIES = 1
    DELAY = 1  # seconds

    def run(self, result):
        for attempt in range(self.RETRIES + 1):
            super().run(result)
            sleep(self.DELAY)


class VersionTest(RetryTestCase):
    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(main, ['--version'])
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, 'launchable-cli, version {}\n'.format(__version__))
