import gzip
import json
import os
import tempfile
from pathlib import Path
from unittest import mock

import responses  # type: ignore

from launchable.test_runners import maven
from launchable.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class MavenTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath('../data/maven/').resolve()

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
        result = self.cli('subset', '--target', '10%', '--session',
                          self.session, 'maven', str(self.test_files_dir.joinpath('java/test/src/java/').resolve()))
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(responses.calls[0].request.body).decode())

        expected = self.load_json_from_file(self.test_files_dir.joinpath('subset_result.json'))

        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_from_file(self):
        # if we prepare listed file with slash e.g) com/example/launchable/model/aModelATest.class
        # the test will be failed at Windows environment. So, we generate file
        # path list
        def save_file(list, file_name):
            file = str(self.test_files_dir.joinpath(file_name))
            with open(file, 'w+') as file:
                for l in list:
                    file.write(l.replace(".", os.path.sep) + ".class\n")

        list_1 = ["com.example.launchable.model.a.ModelATest",
                  "com.example.launchable.model.b.ModelBTest",
                  "com.example.launchable.model.b.ModelBTest$SomeInner",
                  "com.example.launchable.model.c.ModelCTest",

                  ]

        list_2 = ["com.example.launchable.service.ServiceATest",
                  "com.example.launchable.service.ServiceATest$Inner1$Inner2",
                  "com.example.launchable.service.ServiceBTest",
                  "com.example.launchable.service.ServiceCTest",
                  ]

        save_file(list_1, "createdFile_1.lst")
        save_file(list_2, "createdFile_2.lst")

        result = self.cli('subset',
                          '--target',
                          '10%',
                          '--session',
                          self.session,
                          'maven',
                          "--test-compile-created-file",
                          str(self.test_files_dir.joinpath("createdFile_1.lst")),
                          "--test-compile-created-file",
                          str(self.test_files_dir.joinpath("createdFile_2.lst")))
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(responses.calls[0].request.body).decode())

        expected = self.load_json_from_file(self.test_files_dir.joinpath('subset_from_file_result.json'))

        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_by_absolute_time(self):
        result = self.cli('subset', '--time', '1h30m', '--session',
                          self.session, 'maven', str(self.test_files_dir.joinpath('java/test/src/java/').resolve()))
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(responses.calls[0].request.body).decode())

        expected = self.load_json_from_file(self.test_files_dir.joinpath('subset_by_absolute_time_result.json'))

        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_by_confidence(self):
        result = self.cli('subset', '--confidence', '90%', '--session',
                          self.session, 'maven', str(self.test_files_dir.joinpath('java/test/src/java/').resolve()))
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(responses.calls[0].request.body).decode())

        expected = self.load_json_from_file(self.test_files_dir.joinpath('subset_by_confidence_result.json'))

        self.assert_json_orderless_equal(expected, payload)

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
                    [{'type': 'class',
                      'name': 'com.launchableinc.example.App2Test'}],
                    [{'type': 'class',
                      'name': 'com.launchableinc.example.AppTest'}],
                ],
                "rest": [],
            },
            status=200,
        )

        same_bin_file = tempfile.NamedTemporaryFile(delete=False)
        same_bin_file.write(
            b'com.launchableinc.example.AppTest\n'
            b'com.launchableinc.example.App2Test\n'
        )
        result = self.cli(
            'split-subset',
            '--subset-id',
            'subset/456',
            '--bin',
            '1/2',
            "--same-bin",
            same_bin_file.name,
            'maven',
        )

        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            "com.launchableinc.example.App2Test\n"
            "com.launchableinc.example.AppTest",
            result.output.rstrip("\n")
        )

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_maven(self):
        result = self.cli('record', 'tests', '--session', self.session,
                          'maven', str(self.test_files_dir) + "/**/reports")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(responses.calls[1].request.body).decode())

        for e in payload["events"]:
            del e["created_at"]

        expected = self.load_json_from_file(self.test_files_dir.joinpath("record_test_result.json"))

        self.assert_json_orderless_equal(expected, payload)

    def test_glob(self):
        for x in [
            'foo/BarTest.java',
            'foo/BarTest.class',
            'FooTest.class',
            'TestFoo.class',
        ]:
            self.assertTrue(maven.is_file(x))

        for x in [
            'foo/Bar$Test.class',
            'foo/MyTest$Inner.class',
            'foo/Util.class',
        ]:
            self.assertFalse(maven.is_file(x))
