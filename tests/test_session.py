from unittest import TestCase

from launchable.utils.exceptions import ParseSessionException
from launchable.utils.session import parse_session, validate_session_format


class SessionTestClass(TestCase):
    build_name = '123'
    session_id = '/intake/organizations/launchableinc/workspaces/mothership/builds/123/test_sessions/13'

    def test_parse_session(self):
        session = "builds/build-name/test_sessions/123"
        build_name, session_id = parse_session(session)
        self.assertEqual(build_name, "build-name")
        self.assertEqual(session_id, "123")

        with self.assertRaises(Exception):
            parse_session("hoge/fuga")

    def test_validate_session_format(self):
        # Test with a valid session format
        validate_session_format("builds/build-name/test_sessions/123")

        # Test with invalid session formats
        invalid_sessions = [
            "123",                                              # Only id
            "workspaces/mothership/builds/123/test_sessions/13"  # Too many parts
        ]

        for invalid_session in invalid_sessions:
            with self.assertRaises(ParseSessionException):
                validate_session_format(invalid_session)
