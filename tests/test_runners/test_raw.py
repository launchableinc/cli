import gzip
import json
import os
import tempfile
from unittest import mock

import responses  # type: ignore
from launchable.utils.http_client import get_base_url
from launchable.utils.session import write_build
from tests.cli_test_case import CliTestCase
from tests.helper import ignore_warnings


class RawTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
        responses.replace(
            responses.POST,
            "{}/intake/organizations/{}/workspaces/{}/subset".format(
                get_base_url(), self.organization, self.workspace),
            json={
                "testPaths": [
                    [{'type': 'testcase', 'name': 'FooTest.Bar'}],
                    [{'type': 'testcase', 'name': 'FooTest.Foo'}],
                ],
                "testRunner": "raw",
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
            test_path_file = os.path.join(tempdir, 'tests.txt')
            with open(test_path_file, 'w') as f:
                f.write('\n'.join([
                    'testcase=FooTest.Bar',
                    'testcase=FooTest.Foo',
                    '# This is a comment',
                    'testcase=FooTest.Baz',
                ]) + '\n')

            # emulate launchable record build
            write_build(self.build_name)

            result = self.cli('subset', '--target', '10%',
                              'raw', test_path_file, mix_stderr=False)
            self.assertEqual(result.exit_code, 0)

            # Check request body
            payload = json.loads(gzip.decompress(
                responses.calls[1].request.body).decode())
            self.assert_json_orderless_equal(payload, {
                'testPaths': [
                    [{'type': 'testcase', 'name': 'FooTest.Bar'}],
                    [{'type': 'testcase', 'name': 'FooTest.Foo'}],
                    [{'type': 'testcase', 'name': 'FooTest.Baz'}]
                ],
                'testRunner': 'raw',
                'session': {'id': str(self.session_id)},
                "goal": {"type": "subset-by-percentage", "percentage": 0.1},
                "ignoreNewTests": False,
                "getTestsFromPreviousSessions": False,
            })
            # Check split output
            self.assertEqual(result.stdout, '\n'.join([
                'testcase=FooTest.Bar',
                'testcase=FooTest.Foo',
            ]) + '\n')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_tests(self):
        with tempfile.TemporaryDirectory() as tempdir:
            test_path_file = os.path.join(tempdir, 'tests.json')
            with open(test_path_file, 'w') as f:
                f.write('\n'.join([
                    '{',
                    '  "testCases": [',
                    '     {',
                    '       "testPath": "file=a.py#class=classA",',
                    '       "duration": 42,',
                    '       "status": "TEST_PASSED",',
                    '       "stdout": "This is stdout",',
                    '       "stderr": "This is stderr",',
                    '       "createdAt": "2021-10-05T12:34:00"',
                    '     }',
                    '  ]',
                    '}',
                ]) + '\n')

            # emulate launchable record build
            write_build(self.build_name)

            result = self.cli('record', 'tests', 'raw',
                              test_path_file, mix_stderr=False)
            self.assertEqual(result.exit_code, 0)

            # Check request body
            payload = json.loads(gzip.decompress(
                responses.calls[2].request.body).decode())
            self.assert_json_orderless_equal(payload, {
                'events': [
                    {
                        'testPath': [
                            {'type': 'file', 'name': 'a.py'},
                            {'type': 'class', 'name': 'classA'},
                        ],
                        'duration': 42,
                        'status': 1,
                        'stdout': 'This is stdout',
                        'stderr': 'This is stderr',
                        'created_at': '2021-10-05T12:34:00',
                        'data': None,
                        'type': 'case',
                    },
                ],
                "testRunner": "raw"
            })

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    @ignore_warnings
    def test_split_subset(self):
        responses.replace(
            responses.POST,
            "{}/intake/organizations/{}/workspaces/{}/subset/456/slice".format(
                get_base_url(), self.organization, self.workspace),
            json={
                "testPaths": [
                    [{'type': 'testcase', 'name': 'FooTest.Bar'}],
                    [{'type': 'testcase', 'name': 'FooTest.Foo'}],
                ],
                "rest": [[{'type': 'testcase', 'name': 'FooTest.Baz'}]],
            },
            status=200)

        rest = tempfile.NamedTemporaryFile(delete=False)
        result = self.cli(
            'split-subset',
            '--subset-id',
            'subset/456',
            '--bin',
            '1/2',
            '--rest',
            rest.name,
            'raw')

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.stdout,
            '\n'.join([
                'testcase=FooTest.Bar',
                'testcase=FooTest.Foo\n',
            ]))
        self.assertEqual(
            rest.read().decode(),
            'testcase=FooTest.Baz',
        )
        rest.close()
        os.unlink(rest.name)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_split_subset_with_same_bin(self):
        # This test must raise error.
        responses.replace(
            responses.POST,
            "{}/intake/organizations/{}/workspaces/{}/subset/456/slice".format(
                get_base_url(), self.organization, self.workspace),
            json={
                "testPaths": [
                    [{'type': 'testcase', 'name': 'FooTest.Bar'}],
                    [{'type': 'testcase', 'name': 'FooTest.Foo'}],
                ],
                "rest": [],
            },
            status=200)

        same_bin_file = tempfile.NamedTemporaryFile(delete=False)
        same_bin_file.write(
            b'FooTest.Bar\n'
            b'FooTest.Foo')
        result = self.cli(
            'split-subset',
            '--subset-id',
            'subset/456',
            '--bin',
            '1/2',
            "--same-bin",
            same_bin_file.name,
            'raw')
        self.assertTrue(
            "--same-bin option is supported only for gradle test and go-test." in result.stdout)
        same_bin_file.close()
        os.unlink(same_bin_file.name)
