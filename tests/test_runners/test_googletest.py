import gzip
import json
import os
from pathlib import Path
from unittest import mock

import responses
from launchable.utils.http_client import get_base_url  # type: ignore
from tests.cli_test_case import CliTestCase


class GoogleTestTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath(
        '../data/googletest/').resolve()

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
        # I use "ctest -N" to get this list.
        pipe = """FooTest.
  Bar
  Baz
  Foo
        """
        result = self.cli('subset', '--target', '10%',
                          '--session', self.session, 'googletest', input=pipe)
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[0].request.body).decode())
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('subset_result.json'))
        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_googletest(self):
        result = self.cli('record', 'tests',  '--session', self.session,
                          'googletest', str(self.test_files_dir) + "/")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[1].request.body).decode())
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('record_test_result.json'))

        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_failed_test_googletest(self):
        # ./test_a --gtest_output=xml:output.xml
        result = self.cli('record', 'tests',  '--session', self.session,
                          'googletest', str(self.test_files_dir) + "/fail/")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[1].request.body).decode())
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('fail/record_test_result.json'))

        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_empty_dir(self):
        responses.replace(
            responses.GET,
            "{base}/intake/organizations/{org}/workspaces/{ws}/builds/{build_name}".format(
                base=get_base_url(),
                org=self.organization,
                ws=self.workspace,
                build_name=self.build_name),
            json={
                "createdAt": "2022-02-03T04:56:00.789+00:00",
                "buildNumber": self.build_name,
            },
            status=200,
        )

        path = 'latest/gtest_*_results.xml'
        result = self.cli('record', 'tests',  '--session', self.session,
                          'googletest', path)
        self.assertEqual(result.output.rstrip(
            '\n'), "No matches found: {}".format(path))
        self.assertEqual(result.exit_code, 0)
