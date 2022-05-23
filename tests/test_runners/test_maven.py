from pathlib import Path
from unittest import mock
import responses  # type: ignore
import json
import gzip
import os
from tests.cli_test_case import CliTestCase


class MavenTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath(
        '../data/maven/').resolve()

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
        result = self.cli('subset', '--target', '10%', '--session',
                          self.session, 'maven', str(self.test_files_dir.joinpath('java/test/src/java/').resolve()))
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[0].request.body).decode())

        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('subset_result.json'))

        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_from_file(self):
        # if we prepare file list with slash e.g) com/example/launchable/model/aModelATest.java
        # the test will be failed at Windows environment. So, we generate file path list
        list = ["com.example.launchable.model.a.ModelATest",
                "com.example.launchable.model.b.ModelBTest",
                "com.example.launchable.model.c.ModelCTest",
                ]
        generated_lst_file = str(self.test_files_dir.joinpath("list.lst"))
        with open(generated_lst_file, 'w+') as file:
            for l in list:
                file.write(l.replace(".", os.path.sep) + ".java\n")

        result = self.cli('subset', '--target', '10%', '--session',
                          self.session, 'maven', "--from-file", str(self.test_files_dir.joinpath("list_1.txt")), "--from-file", generated_lst_file)
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[0].request.body).decode())

        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('subset_from_file_result.json'))

        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_by_absolute_time(self):
        result = self.cli('subset', '--time', '1h30m', '--session',
                          self.session, 'maven', str(self.test_files_dir.joinpath('java/test/src/java/').resolve()))
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[0].request.body).decode())

        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('subset_by_absolute_time_result.json'))

        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_by_confidence(self):
        result = self.cli('subset', '--confidence', '90%', '--session',
                          self.session, 'maven', str(self.test_files_dir.joinpath('java/test/src/java/').resolve()))
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[0].request.body).decode())

        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('subset_by_confidence_result.json'))

        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_maven(self):
        result = self.cli('record', 'tests',  '--session', self.session,
                          'maven', str(self.test_files_dir) + "/**/reports")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[1].request.body).decode())

        for e in payload["events"]:
            del e["created_at"]

        expected = self.load_json_from_file(
            self.test_files_dir.joinpath("record_test_result.json"))

        self.assert_json_orderless_equal(expected, payload)
