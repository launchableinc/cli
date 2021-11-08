from unittest import TestCase, mock
from launchable.utils.session import write_session, read_session, remove_session, clean_session_files, parse_session, write_build, read_build, SESSION_DIR_KEY
import os
import tempfile


class SessionTestClass(TestCase):
    build_name = '123'
    session_id = '/intake/organizations/launchableinc/workspaces/mothership/builds/123/test_sessions/13'

    def setUp(self):
        dir = tempfile.mkdtemp()
        os.environ[SESSION_DIR_KEY] = dir

    def tearDown(self):
        clean_session_files()
        del os.environ[SESSION_DIR_KEY]

    def test_write_and_read_build(self):
        write_build(self.build_name)
        self.assertEqual(read_build(), self.build_name)

        write_build(self.build_name)
        self.assertEqual(read_build(), self.build_name)

        # got wrror when test session file that another build name is already exists
        with self.assertRaises(Exception):
            write_build('234')

    def test_write_read_remove(self):
        write_session(self.build_name, self.session_id)
        self.assertEqual(read_session(self.build_name), self.session_id)

        remove_session(self.build_name)
        self.assertEqual(read_session(self.build_name), None)

    def test_other_build(self):
        write_session(self.build_name, self.session_id)

        next_build_name = '124'
        next_session_id = '/intake/organizations/launchableinc/workspaces/mothership/builds/123/test_sessions/14'

        # Can't write session if the session file already exists
        with self.assertRaises(Exception):
            write_session(next_build_name, next_session_id)

        # mock record tests command to delete session file
        clean_session_files()

        write_session(next_build_name, next_session_id)
        self.assertEqual(read_session(next_build_name), next_session_id)

    def test_read_before_write(self):
        self.assertEqual(read_session(self.build_name), None)

    def test_different_pid(self):
        # TODO
        pass

    def test_parse_session(self):
        session = "builds/build-name/test_sessions/123"
        build_name, session_id = parse_session(session)
        self.assertEqual(build_name, "build-name")
        self.assertEqual(session_id, "123")

        with self.assertRaises(Exception):
            parse_session("hoge/fuga")
