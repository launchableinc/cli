import gzip
import json
import os
import sys
from pathlib import Path
from unittest import mock

import responses  # type: ignore

from launchable.commands.record.tests import INVALID_TIMESTAMP, parse_launchable_timeformat, summarize_case_events
from launchable.utils.http_client import get_base_url
from launchable.utils.link import LinkKind
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

        self.assert_success(result)
        request = json.loads(gzip.decompress(self.find_request('/events').request.body).decode())
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
        self.assertIn('open_class_user_test.rb', gzip.decompress(self.find_request('/events').request.body).decode())

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

    def _case_event(self, test_path, status, duration=0.0):
        return {"type": "case", "testPath": test_path, "status": status, "duration": duration,
                "stdout": "", "stderr": "", "data": None}

    def test_summarize_case_events_single_event_per_test(self):
        """One event per test (the common case, unaffected by flaky/rerun expansion)."""
        passing_path = [{"type": "class", "name": "AppTest"}, {"type": "testcase", "name": "shouldWork"}]
        failing_path = [{"type": "class", "name": "BrokenTest"}, {"type": "testcase", "name": "neverWorks"}]
        events = [
            self._case_event(passing_path, status=1, duration=0.01),
            self._case_event(failing_path, status=0, duration=0.02),
        ]

        test_count, success_count, fail_count, duration = summarize_case_events(events)

        self.assertEqual((test_count, success_count, fail_count), (2, 1, 1))
        self.assertAlmostEqual(duration, (0.01 + 0.02) / 60)

    def test_summarize_case_events_rerun_counts_as_one_test(self):
        """A flaky test (4 FAILED attempts + 1 final PASSED, same testPath) must count as ONE
        test, not five -- this is exactly the bug the raw per-event counting had."""
        flaky_path = [{"type": "class", "name": "FlakyTest"}, {"type": "testcase", "name": "passesEventually"}]
        events = [self._case_event(flaky_path, status=0, duration=0.0) for _ in range(4)]
        events.append(self._case_event(flaky_path, status=1, duration=0.045))

        test_count, success_count, fail_count, duration = summarize_case_events(events)

        self.assertEqual((test_count, success_count, fail_count), (1, 1, 0))
        self.assertAlmostEqual(duration, 0.045 / 60)

    def test_summarize_case_events_normal_and_rerun_mixed(self):
        """A normal test (1 event, PASSED) plus a rerun-fail test (5 events, all FAILED, same
        testPath) should report 2 tests found / 1 passed / 1 failed -- not 6 / 1 / 5."""
        normal_path = [{"type": "class", "name": "AppTest"}, {"type": "testcase", "name": "shouldWork"}]
        rerun_fail_path = [{"type": "class", "name": "AlwaysFailingTest"}, {"type": "testcase", "name": "neverPasses"}]
        events = [self._case_event(normal_path, status=1, duration=0.002)]
        events.append(self._case_event(rerun_fail_path, status=0, duration=0.001))
        events.extend(self._case_event(rerun_fail_path, status=0, duration=0.0) for _ in range(4))

        test_count, success_count, fail_count, duration = summarize_case_events(events)

        self.assertEqual((test_count, success_count, fail_count), (2, 1, 1))
        self.assertAlmostEqual(duration, (0.002 + 0.001) / 60)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_when_total_test_duration_zero(self):
        write_build(self.build_name)

        zero_duration_xml1 = str(Path(__file__).parent.joinpath('../../data/googletest/output_a.xml').resolve())
        zero_duration_xml2 = str(Path(__file__).parent.joinpath('../../data/googletest/output_b.xml').resolve())
        result = self.cli('record', 'tests', '--build', self.build_name, 'googletest', zero_duration_xml1, zero_duration_xml2)

        self.assert_success(result)
        self.assertIn("Total test duration is 0.", result.output)

    @responses.activate
    @mock.patch.dict(os.environ, {
        "LAUNCHABLE_TOKEN": CliTestCase.launchable_token,
        "GITHUB_PULL_REQUEST_URL": "https://github.com/launchableinc/cli/pull/1",
    }, clear=True)
    def test_with_links(self):
        # Endpoint to assert
        endpoint = "{}/intake/organizations/{}/workspaces/{}/builds/{}/test_sessions".format(
            get_base_url(),
            self.organization,
            self.workspace,
            self.build_name)

        # Capture from environment
        write_build(self.build_name)
        result = self.cli("record", "tests", "--build", self.build_name, 'maven', str(self.report_files_dir) + "**/reports/")
        self.assert_success(result)
        payload = json.loads(self.find_request(endpoint, 0).request.body.decode())
        self.assertEqual([{
            "kind": LinkKind.GITHUB_PULL_REQUEST.name,
            "title": "",
            "url": "https://github.com/launchableinc/cli/pull/1",
        }], payload["links"])

        # Priority check
        write_build(self.build_name)
        result = self.cli("record", "tests", "--build", self.build_name, "--link",
                          "GITHUB_PULL_REQUEST|PR=https://github.com/launchableinc/cli/pull/2", 'maven',
                          str(self.report_files_dir) + "**/reports/")
        self.assert_success(result)
        payload = json.loads(self.find_request(endpoint, 1).request.body.decode())
        self.assertEqual([{
            "kind": LinkKind.GITHUB_PULL_REQUEST.name,
            "title": "PR",
            "url": "https://github.com/launchableinc/cli/pull/2",
        }], payload["links"])

        # Infer kind
        write_build(self.build_name)
        result = self.cli("record",
                          "tests",
                          "--build",
                          self.build_name,
                          "--link",
                          "PR=https://github.com/launchableinc/cli/pull/2",
                          'maven',
                          str(self.report_files_dir) + "**/reports/")
        self.assert_success(result)
        payload = json.loads(self.find_request(endpoint, 2).request.body.decode())
        self.assertEqual([{
            "kind": LinkKind.GITHUB_PULL_REQUEST.name,
            "title": "PR",
            "url": "https://github.com/launchableinc/cli/pull/2",
        }], payload["links"])

        # Explicit kind
        write_build(self.build_name)
        result = self.cli("record", "tests", "--build", self.build_name, "--link",
                          "GITHUB_PULL_REQUEST|PR=https://github.com/launchableinc/cli/pull/2", 'maven',
                          str(self.report_files_dir) + "**/reports/")
        self.assert_success(result)
        payload = json.loads(self.find_request(endpoint, 3).request.body.decode())
        self.assertEqual([{
            "kind": LinkKind.GITHUB_PULL_REQUEST.name,
            "title": "PR",
            "url": "https://github.com/launchableinc/cli/pull/2",
        }], payload["links"])

        # Invalid kind
        write_build(self.build_name)
        result = self.cli("record",
                          "tests",
                          "--build",
                          self.build_name,
                          "--link",
                          "UNKNOWN_KIND|PR=https://github.com/launchableinc/cli/pull/2",
                          'maven',
                          str(self.report_files_dir) + "**/reports/")
        self.assertIn("Invalid kind 'UNKNOWN_KIND' passed to --link option", result.output)

        # Invalid URL
        write_build(self.build_name)
        result = self.cli("record", "tests", "--build", self.build_name, "--link",
                          "GITHUB_PULL_REQUEST|PR=https://github.com/launchableinc/cli/pull/2/files", 'maven',
                          str(self.report_files_dir) + "**/reports/")
        self.assertIn("Invalid url 'https://github.com/launchableinc/cli/pull/2/files' passed to --link option", result.output)

        # With --session flag
        write_session(self.build_name, self.session)
        result = self.cli("record", "tests", "--session", self.session, "--link",
                          "GITHUB_PULL_REQUEST|PR=https://github.com/launchableinc/cli/pull/2/files", 'maven',
                          str(self.report_files_dir) + "**/reports/")
        self.assertIn("WARNING: `--link` and `--session` are set together", result.output)
        self.assert_success(result)

        # Existing session
        write_session(self.build_name, self.session)
        result = self.cli("record", "tests", "--link",
                          "GITHUB_PULL_REQUEST|PR=https://github.com/launchableinc/cli/pull/2/files", 'maven',
                          str(self.report_files_dir) + "**/reports/")
        self.assertIn("WARNING: --link option is ignored since session already exists", result.output)
        self.assert_success(result)
