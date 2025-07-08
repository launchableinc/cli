import gzip
import json
import os
import sys
from pathlib import Path
from unittest import mock

import responses  # type: ignore

from smart_tests.commands.record.tests import INVALID_TIMESTAMP, parse_launchable_timeformat
from smart_tests.utils.http_client import get_base_url
from smart_tests.utils.no_build import NO_BUILD_BUILD_NAME, NO_BUILD_TEST_SESSION_ID
from tests.cli_test_case import CliTestCase


class TestsTest(CliTestCase):
    report_files_dir = Path(__file__).parent.joinpath(
        '../../data/maven/').resolve()

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_with_group_name(self):
        # Test uses explicit session parameter
        # Override the base 404 response to allow session lookup to succeed
        responses.replace(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/{self.workspace}"
            f"/builds/{self.build_name}/test_session_names/{self.session_name}",
            json={
                'id': self.session_id,
                'isObservation': False,
            },
            status=200)

        result = self.cli('record', 'test', 'maven', '--build', self.build_name, '--session',
                          self.session_name, '--group', 'hoge', str(
                              self.report_files_dir) + "**/reports/")

        self.assert_success(result)
        request = json.loads(gzip.decompress(self.find_request('/events').request.body).decode())
        self.assertCountEqual(request.get("group", []), "hoge")

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_filename_in_error_message(self):
        # emulate launchable record build
        # Override the base 404 response to allow session lookup to succeed
        responses.replace(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/{self.workspace}"
            f"/builds/{self.build_name}/test_session_names/{self.session_name}",
            json={
                'id': self.session_id,
                'isObservation': False,
            },
            status=200)

        normal_xml = str(Path(__file__).parent.joinpath('../../data/broken_xml/normal.xml').resolve())
        broken_xml = str(Path(__file__).parent.joinpath('../../data/broken_xml/broken.xml').resolve())
        result = self.cli(
            'record',
            'test',
            'file',
            '--build',
            self.build_name,
            '--session',
            self.session_name,
            normal_xml,
            broken_xml)

        def remove_backslash(input: str) -> str:
            # Hack for Windowns. They containts double escaped backslash such
            # as \\\\
            if sys.platform == "win32":
                return input.replace("\\", "")
            else:
                return input

        # making sure the offending file path name is being printed.
        self.assertIn(remove_backslash(broken_xml), remove_backslash(result.output))

        # normal.xml
        self.assertIn('open_class_user_test.rb', gzip.decompress(self.find_request('/events').request.body).decode())

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_with_no_build(self):
        responses.add(
            responses.POST,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/"
            f"{self.workspace}/builds/{NO_BUILD_BUILD_NAME}/test_sessions/{NO_BUILD_TEST_SESSION_ID}/events",
            json={
                "build": {
                    "id": 12345,
                    "buildNumber": 1675750000,
                },
                "testSessions": {
                    "id": 678,
                    "buildId": 12345,
                },
            },
            status=200)

        result = self.cli('record', 'test', 'maven', '--no-build', '--session',
                          self.session_name, str(self.report_files_dir) + "**/reports/")
        self.assert_success(result)

    def test_parse_launchable_timeformat(self):
        t1 = "2021-04-01T09:35:47.934+00:00"  # 1617269747.934
        t2 = "2021-05-24T18:29:04.285+00:00"  # 1621880944.285
        t3 = "2021-05-32T26:29:04.285+00:00"  # invalid time format

        parse_launchable_time1 = parse_launchable_timeformat(t1)
        parse_launchable_time2 = parse_launchable_timeformat(t2)

        self.assertEqual(parse_launchable_time1.timestamp(), 1617269747.934)
        self.assertEqual(parse_launchable_time2.timestamp(), 1621880944.285)

        self.assertEqual(INVALID_TIMESTAMP, parse_launchable_timeformat(t3))
