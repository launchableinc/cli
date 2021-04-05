from unittest import TestCase
from launchable.commands.helper import _validate_session_and_build_name
import click


class TestHelper(TestCase):

    def test__validate_session_and_build_name(self):
        with self.assertRaises(click.UsageError):
            _validate_session_and_build_name(None, None)

        with self.assertRaises(click.UsageError):
            _validate_session_and_build_name("session", "build_name")

        _validate_session_and_build_name("session", None)
        _validate_session_and_build_name(None, "build_name")
