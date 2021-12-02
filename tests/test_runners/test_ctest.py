from pathlib import Path
import responses  # type: ignore
import json
import gzip
import os
import sys
import tempfile
from launchable.utils.session import read_session, write_build
from launchable.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase
from unittest import mock


class CTestTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath(
        '../data/ctest/').resolve()

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_multiple_files(self):
        responses.replace(
            responses.POST,
            "{}/intake/organizations/{}/workspaces/{}/subset".format(
                get_base_url(), self.organization, self.workspace),
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

            # emulate launchable record build
            write_build(self.build_name)

            result = self.cli('subset', '--target', '10%', 'ctest',
                              '--output-regex-files',
                              '--output-regex-files-dir=' + output_dir,
                              '--output-regex-files-size=32',
                              str(self.test_files_dir.joinpath("ctest_list.json")))
            self.assertEqual(result.exit_code, 0)

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
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_without_session(self):
        # emulate launchable record build
        write_build(self.build_name)

        result = self.cli('subset', '--target', '10%', 'ctest',
                          str(self.test_files_dir.joinpath("ctest_list.json")))
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[1].request.body).decode())
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('subset_result.json'))
        self.assert_json_orderless_equal(payload, expected)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test(self):
        # emulate launchable record build
        write_build(self.build_name)

        result = self.cli('record', 'tests', 'ctest', str(
            self.test_files_dir) + "/Testing/**/Test.xml")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(read_session(self.build_name), self.session)

        payload = json.loads(gzip.decompress(
            responses.calls[2].request.body).decode())
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('record_test_result.json'))

        for c in payload['events']:
            del c['created_at']
        self.assert_json_orderless_equal(payload, expected)
