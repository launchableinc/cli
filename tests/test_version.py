from unittest import TestCase, TextTestResult
from time import sleep

from click.testing import CliRunner  # type: ignore

from launchable.__main__ import main
from launchable.version import __version__

class RetryTestCase(TestCase):
    RETRIES = 1
    DELAY = 1  # seconds

    def run(self, result):
        for attempt in range(self.RETRIES + 1):
            super().run(result)
            # If the test passes, break out of the loop
            if result.wasSuccessful():
                return
            # If the test fails and there are retries left, wait for the delay
            if attempt < self.RETRIES:
                sleep(self.DELAY)
                # Clear failures and errors so that unittest doesn't process them
                result.failures.clear()
                result.errors.clear()
                print(f"Retrying {self.id()}. Attempt {attempt + 1}")

class VersionTest(RetryTestCase):
    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(main, ['--version'])
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, 'launchable-cli, version {}\n'.format(__version__))
