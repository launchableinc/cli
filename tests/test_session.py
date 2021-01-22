from unittest import TestCase
from launchable.utils.session import write_session, read_session, remove_session, clean_session_files


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
