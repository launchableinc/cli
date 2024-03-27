import os
import tempfile
from unittest import mock

import responses  # type: ignore

from launchable.utils.http_client import get_base_url
from launchable.utils.session import read_session, write_build
from tests.cli_test_case import CliTestCase


class GoTestTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_with_session(self):
        pipe = "TestExample1\nTestExample2\nTestExample3\nTestExample4\n" \
               "ok      github.com/launchableinc/rocket-car-gotest      0.268s"
        result = self.cli('subset', '--target', '10%', '--session', self.session, 'go-test', input=pipe)
        self.assert_success(result)
        self.assert_subset_payload('subset_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_without_session(self):
        # emulate launchable record build
        write_build(self.build_name)

        pipe = "TestExample1\nTestExample2\nTestExample3\nTestExample4\n" \
               "ok      github.com/launchableinc/rocket-car-gotest      0.268s"
        result = self.cli('subset', '--target', '10%', 'go-test', input=pipe)

        self.assert_success(result)

        self.assertEqual(read_session(self.build_name), self.session)
        self.assert_subset_payload('subset_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_tests_with_session(self):
        result = self.cli('record', 'tests', '--session',
                          self.session, 'go-test', str(self.test_files_dir.joinpath('reportv1')) + "/")
        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_tests_without_session(self):
        # emulate launchable record build
        write_build(self.build_name)

        result = self.cli('record', 'tests', 'go-test', str(self.test_files_dir.joinpath('reportv1')) + "/")
        self.assert_success(result)

        self.assertEqual(read_session(self.build_name), self.session)
        self.assert_record_tests_payload('record_test_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_tests_v2(self):
        result = self.cli('record', 'tests', '--session',
                          self.session, 'go-test', str(self.test_files_dir.joinpath('reportv2')) + "/")
        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_split_subset_with_same_bin(self):
        responses.replace(
            responses.POST,
            "{}/intake/organizations/{}/workspaces/{}/subset/456/slice".format(
                get_base_url(),
                self.organization,
                self.workspace,
            ),
            json={
                'testPaths': [
                    [
                        {'type': 'class', 'name': 'rocket-car-gotest'},
                        {'type': 'testcase', 'name': 'TestExample1'},
                    ],
                    [
                        {'type': 'class', 'name': 'rocket-car-gotest'},
                        {'type': 'testcase', 'name': 'TestExample2'},
                    ],
                ],
                "rest": [],
            },
            status=200,
        )

        same_bin_file = tempfile.NamedTemporaryFile(delete=False)
        same_bin_file.write(
            b'rocket-car-gotest.TestExample1\n'
            b'rocket-car-gotest.TestExample2')
        result = self.cli(
            'split-subset',
            '--subset-id',
            'subset/456',
            '--bin',
            '1/2',
            "--same-bin",
            same_bin_file.name,
            'go-test',
        )

        self.assert_success(result)

        self.assertEqual("^TestExample1$|^TestExample2$\n", result.output)
        same_bin_file.close()
        os.unlink(same_bin_file.name)
