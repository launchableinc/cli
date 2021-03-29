from unittest import TestCase
from launchable.utils.http_client import LaunchableClient
import platform
from launchable.version import __version__


class LaunchableClientTest(TestCase):
    def test_header(self):
        cli = LaunchableClient("test", "/test")
        self.assertEqual(cli._headers(), {
            "Authorization": "Bearer test",
            "User-Agent": "Launchable/{} (Python {}, {})".format(__version__, platform.python_version(), platform.platform()),
        })

        cli = LaunchableClient("test", "/test", test_runner="dummy")
        self.assertEqual(cli._headers(), {
            "Authorization": "Bearer test",
            "User-Agent": "Launchable/{} (Python {}, {})".format(__version__, platform.python_version(), platform.platform()),
            "launchable-test-runner": "dummy"
        })
