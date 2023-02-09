import gzip
import json
import os
import sys
from pathlib import Path
from unittest import mock

import responses  # type: ignore

from launchable.commands.record.tests import INVALID_TIMESTAMP, parse_launchable_timeformat
from launchable.utils.http_client import get_base_url
from launchable.utils.no_build import NO_BUILD_BUILD_NAME, NO_BUILD_TEST_SESSION_ID
from launchable.utils.session import write_build, write_session
from tests.cli_test_case import CliTestCase


class TestsTest(CliTestCase):
    report_files_dir = Path(__file__).parent.joinpath(
        '../../data/maven/').resolve()

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_with_group_name(self):
        # emulate launchable record build & session
        write_session(self.build_name, self.session_id)

        result = self.cli('record', 'tests', '--session',
                          self.session, '--group', 'hoge', 'maven', str(
                              self.report_files_dir) + "**/reports/")

        self.assertEqual(result.exit_code, 0)
        # get request body
        # responses.calls[0]: GET: build information
        # responses.calls[1]: POST: record tests
        request = json.loads(gzip.decompress(
            responses.calls[1].request.body).decode())

        self.assertCountEqual(request.get("group", []), "hoge")

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_filename_in_error_message(self):
        # emulate launchable record build
        write_build(self.build_name)

        normal_xml = str(Path(__file__).parent.joinpath('../../data/broken_xml/normal.xml').resolve())
        broken_xml = str(Path(__file__).parent.joinpath('../../data/broken_xml/broken.xml').resolve())
        result = self.cli('record', 'tests', '--build', self.build_name, 'file', normal_xml, broken_xml)

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
        self.assertIn('open_class_user_test.rb', gzip.decompress(responses.calls[2].request.body).decode())

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_with_no_build(self):
        responses.add(
            responses.POST,
            "{}/intake/organizations/{}/workspaces/{}/builds/{}/test_sessions/{}/events".format(
                get_base_url(),
                self.organization,
                self.workspace,
                NO_BUILD_BUILD_NAME,
                NO_BUILD_TEST_SESSION_ID,
            ),
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

        result = self.cli('record', 'tests', '--no-build', 'maven', str(self.report_files_dir) + "**/reports/")
        self.assertEqual(result.exit_code, 0)

    def test_parse_launchable_timeformat(self):
        t1 = "2021-04-01T09:35:47.934+00:00"  # 1617269747.934
        t2 = "2021-05-24T18:29:04.285+00:00"  # 1621880944.285
        t3 = "2021-05-32T26:29:04.285+00:00"  # invalid time format

        parse_launchable_time1 = parse_launchable_timeformat(t1)
        parse_launchable_time2 = parse_launchable_timeformat(t2)

        self.assertEqual(parse_launchable_time1.timestamp(), 1617269747.934)
        self.assertEqual(parse_launchable_time2.timestamp(), 1621880944.285)

        self.assertEqual(INVALID_TIMESTAMP, parse_launchable_timeformat(t3))
