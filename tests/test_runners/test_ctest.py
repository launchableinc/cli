import os
import sys
import tempfile
from unittest import mock

import responses  # type: ignore

from smart_tests.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class CTestTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_subset_multiple_files(self):
        # Override session name lookup to allow session resolution
        responses.replace(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/"
            f"{self.workspace}/builds/{self.build_name}/test_session_names/{self.session_name}",
            json={
                'id': self.session_id,
                'isObservation': False,
            },
            status=200)

        responses.replace(
            responses.POST,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/{self.workspace}/subset",
            json={
                "testPaths": [
                    [{'type': 'testcase', 'name': 'FooTest.Bar'}],
                    [{'type': 'testcase', 'name': 'FooTest.Foo'}],
                    [{'type': 'testcase', 'name': '*/ParameterizedTest.Bar/*'}],
                ],
                "rest": [
                    [{'name': 'FooTest.Baz'}],
                ],
                "subsettingId": 456,
                "summary": {
                    "subset": {"candidates": 4, "duration": 4, "rate": 90},
                    "rest": {"candidate": 1, "duration": 0, "rate": 0}
                },
                "isBrainless": False
            },
            status=200)
        with tempfile.TemporaryDirectory() as tempdir:
            # Use a non-existing dir to check it creates a dir.
            output_dir = os.path.join(tempdir, 'subdir')
            result = self.cli('subset', 'ctest', '--session', self.session_name, '--build', self.build_name, '--target', '10%',
                              '--output-regex-files',
                              '--output-regex-files-dir=' + output_dir,
                              '--output-regex-files-size=32',
                              str(self.test_files_dir.joinpath("ctest_list.json")))
            self.assert_success(result)

            subset_files = []
            rest_files = []
            for file in os.listdir(output_dir):
                with open(os.path.join(output_dir, file), 'r') as f:
                    if file.startswith('subset'):
                        subset_files.append(f.read().strip())
                    else:
                        rest_files.append(f.read().strip())
            subset_files.sort()
            rest_files.sort()
            if sys.version_info[:2] >= (3, 7):
                self.assertEqual(subset_files, [
                    '^FooTest\\.Bar$|^FooTest\\.Foo$',
                    '^\\*/ParameterizedTest\\.Bar/\\*$'
                ])
            else:
                # There was a change in re.escape behavior from Python 3.7. See
                # https://docs.python.org/3/library/re.html#re.escape
                self.assertEqual(subset_files, [
                    '^FooTest\\.Bar$|^FooTest\\.Foo$',
                    '^\\*\\/ParameterizedTest\\.Bar\\/\\*$'
                ])
            self.assertEqual(rest_files, ['^FooTest\\.Baz$'])

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_subset_without_session(self):
        # Override session name lookup to allow session resolution
        responses.replace(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/"
            f"{self.workspace}/builds/{self.build_name}/test_session_names/{self.session_name}",
            json={
                'id': self.session_id,
                'isObservation': False,
            },
            status=200)

        result = self.cli('subset', 'ctest', '--session', self.session_name, '--build', self.build_name, '--target', '10%',
                          str(self.test_files_dir.joinpath("ctest_list.json")))
        self.assert_success(result)
        self.assert_subset_payload('subset_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_test(self):
        # Override session name lookup to allow session resolution
        responses.replace(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/"
            f"{self.workspace}/builds/{self.build_name}/test_session_names/{self.session_name}",
            json={
                'id': self.session_id,
                'isObservation': False,
            },
            status=200)

        result = self.cli('record', 'test', 'ctest', '--session', self.session_name, '--build',
                          self.build_name, str(self.test_files_dir) + "/Testing/**/Test.xml")
        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')
