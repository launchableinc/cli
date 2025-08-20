import gzip
import itertools
import json
import os
from unittest import mock

import responses  # type: ignore

from tests.cli_test_case import CliTestCase


class BazelTest(CliTestCase):
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
        result = self.cli('subset', '--session', self.session, '--target', '10%', 'bazel', input=self.subset_input)
        self.assert_success(result)
        self.assert_subset_payload('subset_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test(self):
        result = self.cli('record', 'tests', '--session', self.session, 'bazel', str(self.test_files_dir) + "/")
        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_with_build_event_json_file(self):
        result = self.cli('record', 'tests', '--session', self.session, 'bazel', '--build-event-json', str(
            self.test_files_dir.joinpath("build_event.json")), str(self.test_files_dir) + "/")
        self.assert_success(result)
        self.assert_record_tests_payload('record_test_with_build_event_json_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_with_multiple_build_event_json_files(self):
        result = self.cli('record', 'tests', '--session', self.session,
                          'bazel', '--build-event-json',
                          str(self.test_files_dir.joinpath("build_event.json")),
                          '--build-event-json', str(self.test_files_dir.joinpath("build_event_rest.json")),
                          str(self.test_files_dir) + "/")
        self.assert_success(result)
        self.assert_record_tests_payload('record_test_with_multiple_build_event_json_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_record_key_match(self):
        """
        Test recorded test results contain subset's test path
        """
        result = self.cli('subset', '--session', self.session, '--target', '10%', 'bazel', input=self.subset_input)

        self.assert_success(result)

        subset_payload = json.loads(gzip.decompress(self.find_request('/subset').request.body).decode())

        result = self.cli('record', 'tests', '--session', self.session, 'bazel', str(self.test_files_dir) + "/")
        self.assert_success(result)

        record_payload = json.loads(gzip.decompress(self.find_request('/events').request.body).decode())

        record_test_paths = itertools.chain.from_iterable(e['testPath'] for e in record_payload['events'])
        record_test_path_dict = {t['name']: t for t in record_test_paths}

        for test_paths in subset_payload['testPaths']:
            for subset_test_path in test_paths:
                record_test_path = record_test_path_dict.get(subset_test_path['name'])
                self.assert_json_orderless_equal(record_test_path, subset_test_path)
