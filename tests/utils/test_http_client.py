import platform
import os
from unittest import TestCase, mock
from launchable.utils.http_client import LaunchableClient
from launchable.version import __version__


class LaunchableClientTest(TestCase):
    @mock.patch.dict(os.environ, {"LAUNCHABLE_ORGANIZATION": "launchableinc", "LAUNCHABLE_WORKSPACE": "test"}, clear=True)
    def test_header(self):
        cli = LaunchableClient("/test")
        self.assertEqual(cli._headers(True), {
            'Content-Encoding': 'gzip',
            'Content-Type': 'application/json',
            "User-Agent": "Launchable/{} (Python {}, {})".format(__version__, platform.python_version(), platform.platform()),
        })

        self.assertEqual(cli._headers(False), {
            'Content-Type': 'application/json',
            "User-Agent": "Launchable/{} (Python {}, {})".format(__version__, platform.python_version(), platform.platform()),
        })

        cli = LaunchableClient("/test", test_runner="dummy")
        self.assertEqual(cli._headers(False), {
            'Content-Type': 'application/json',
            "User-Agent": "Launchable/{} (Python {}, {}) TestRunner/{}".format(__version__, platform.python_version(), platform.platform(), "dummy"),
        })
