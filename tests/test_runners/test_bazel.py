from pathlib import Path
import responses  # type: ignore
import json
import os
import gzip
import itertools
from launchable.utils.session import read_session, write_build
from tests.cli_test_case import CliTestCase
from unittest import mock


class BazelTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath(
        '../data/bazel/').resolve()
    subset_input = """Starting local Bazel server and connecting to it...
//src/test/java/com/ninjinkun:mylib_test9
//src/test/java/com/ninjinkun:mylib_test8
//src/test/java/com/ninjinkun:mylib_test7
//src/test/java/com/ninjinkun:mylib_test6
//src/test/java/com/ninjinkun:mylib_test5
//src/test/java/com/ninjinkun:mylib_test4
//src/test/java/com/ninjinkun:mylib_test3
//src/test/java/com/ninjinkun:mylib_test2
//src/test/java/com/ninjinkun:mylib_test1
Loading: 2 packages loaded
"""

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
        # emulate launchable record build
        write_build(self.build_name)

        result = self.cli('subset', '--target', '10%',
                          'bazel', input=self.subset_input)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(read_session(self.build_name), self.session)

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

        result = self.cli('record', 'tests', 'bazel',
                          str(self.test_files_dir) + "/")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(read_session(self.build_name), self.session)

        payload = json.loads(gzip.decompress(
            responses.calls[2].request.body).decode())
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('record_test_result.json'))

        for c in payload['events']:
            del c['created_at']

        self.assert_json_orderless_equal(payload, expected)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_with_build_event_json_file(self):
        # emulate launchable record build
        write_build(self.build_name)

        result = self.cli('record', 'tests', 'bazel', '--build-event-json', str(
            self.test_files_dir.joinpath("build_event.json")), str(self.test_files_dir) + "/")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(read_session(self.build_name), self.session)

        payload = json.loads(gzip.decompress(
            responses.calls[2].request.body).decode())
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('record_test_with_build_event_json_result.json'))

        for c in payload['events']:
            del c['created_at']

        self.assert_json_orderless_equal(payload, expected)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_with_multiple_build_event_json_files(self):
        # emulate launchable record build
        write_build(self.build_name)

        result = self.cli('record', 'tests', 'bazel', '--build-event-json', str(self.test_files_dir.joinpath("build_event.json")),
                          '--build-event-json', str(self.test_files_dir.joinpath("build_event_rest.json")), str(self.test_files_dir) + "/")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(read_session(self.build_name), self.session)

        payload = json.loads(gzip.decompress(
            responses.calls[2].request.body).decode())
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('record_test_with_multiple_build_event_json_result.json'))

        for c in payload['events']:
            del c['created_at']

        self.assert_json_orderless_equal(payload, expected)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_record_key_match(self):
        # emulate launchable record build
        write_build(self.build_name)

        """
        Test recorded test results contain subset's test path
        """
        result = self.cli('subset', '--target', '10%',
                          'bazel', input=self.subset_input)

        self.assertEqual(result.exit_code, 0)

        subset_payload = json.loads(gzip.decompress(
            responses.calls[1].request.body).decode())

        result = self.cli('record', 'tests', 'bazel',
                          str(self.test_files_dir) + "/")
        self.assertEqual(result.exit_code, 0)

        record_payload = json.loads(gzip.decompress(
            responses.calls[3].request.body).decode())

        record_test_paths = itertools.chain.from_iterable(
            e['testPath'] for e in record_payload['events'])
        record_test_path_dict = {t['name']: t for t in record_test_paths}

        for test_paths in subset_payload['testPaths']:
            for subset_test_path in test_paths:
                record_test_path = record_test_path_dict.get(
                    subset_test_path['name'])
                self.assert_json_orderless_equal(
                    record_test_path, subset_test_path)
