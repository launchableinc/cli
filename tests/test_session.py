from unittest import TestCase, mock
from launchable.utils.session import write_session, read_session, remove_session, clean_session_files, _get_session_id, parse_session
import os


class SessionTestClass(TestCase):
    build_name = '123'
    session_id = '/intake/organizations/launchableinc/workspaces/mothership/builds/123/test_sessions/13'

    def tearDown(self):
        clean_session_files()

    def test_write_read_remove(self):
        write_session(self.build_name, self.session_id)
        self.assertEqual(read_session(self.build_name), self.session_id)

        remove_session(self.build_name)
        self.assertEqual(read_session(self.build_name), None)

    def test_other_build(self):
        write_session(self.build_name, self.session_id)

        next_build_name = '124'
        next_session_id = '/intake/organizations/launchableinc/workspaces/mothership/builds/123/test_sessions/14'
        write_session(next_build_name, next_session_id)

        self.assertEqual(read_session(next_build_name), next_session_id)
        self.assertEqual(read_session(self.build_name), self.session_id)

    def test_read_before_write(self):
        self.assertEqual(read_session(self.build_name), None)

    def test_different_pid(self):
        # TODO
        pass

    def test_get_session_id(self):
        id = _get_session_id()

        with mock.patch.dict(os.environ, {"CIRCLECI": "TRUE", "CIRCLE_WORKFLOW_ID": "abc-123"}):
            id_in_circleci = _get_session_id()

            self.assertEqual(id_in_circleci, "abc-123")
            self.assertNotEqual(id, id_in_circleci)

    def test_parse_session(self):
        session = "builds/build-name/test_sessions/123"
        build_name, session_id = parse_session(session)
        self.assertEqual(build_name, "build-name")
        self.assertEqual(session_id, "123")

        with self.assertRaises(Exception):
            parse_session("hoge/fuga")
