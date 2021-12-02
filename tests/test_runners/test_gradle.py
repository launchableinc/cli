from pathlib import Path
from unittest import mock
import responses  # type: ignore
import json
import gzip
from launchable.utils.session import write_build
from tests.cli_test_case import CliTestCase
from launchable.utils.http_client import get_base_url
import tempfile
import os
from tests.helper import ignore_warnings


class GradleTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath(
        '../data/gradle/').resolve()
    result_file_path = test_files_dir.joinpath('recursion/expected.json')

    @ignore_warnings
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_without_session(self):
        responses.replace(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(get_base_url(), self.organization, self.workspace),
                          json={
                              "testPaths": [[{'name': 'com.launchableinc.rocket_car_gradle.App2Test'}], [{'name': 'com.launchableinc.rocket_car_gradle.AppTest'}], [{'name': 'com.launchableinc.rocket_car_gradle.sub.App3Test'}], [{'name': 'com.launchableinc.rocket_car_gradle.utils.UtilsTest'}]],
                              "rest": [],
                              "subsettingId": 456,
                              "summary": {
                                  "subset": {"candidates": 4, "duration": 4, "rate": 100},
                                  "rest": {"candidate": 0, "duration": 0, "rate": 0}
                              }, "isBrainless": False},
                          status=200)

        # emulate launchable record build
        write_build(self.build_name)

        result = self.cli('subset', '--target', '10%', 'gradle',
                          str(self.test_files_dir.joinpath('java/app/src/test').resolve()))
        # TODO: we need to assert on the request payload to make sure it found test list all right
        self.assertEqual(result.exit_code, 0)
        output = '--tests com.launchableinc.rocket_car_gradle.App2Test --tests com.launchableinc.rocket_car_gradle.AppTest --tests com.launchableinc.rocket_car_gradle.sub.App3Test --tests com.launchableinc.rocket_car_gradle.utils.UtilsTest'
        self.assertIn(output, result.output.rstrip('\n'))

    @ignore_warnings
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_rest(self):
        responses.replace(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(get_base_url(), self.organization, self.workspace), json={
            "testPaths": [[{'type': 'class', 'name': 'com.launchableinc.rocket_car_gradle.App2Test'}], [{'type': 'class', 'name': 'com.launchableinc.rocket_car_gradle.AppTest'}], [{'type': 'class', 'name': 'com.launchableinc.rocket_car_gradle.utils.UtilsTest'}]],
            "rest": [[{'name': 'com.launchableinc.rocket_car_gradle.sub.App3Test'}]],
            "subsettingId": 456,
            "summary": {
                "subset": {"candidates": 3, "duration": 3, "rate": 75},
                "rest": {"candidate": 1, "duration": 1, "rate": 25}
            },
            "isBrainless": False,
        }, status=200)

        rest = tempfile.NamedTemporaryFile(delete=False)

        # emulate launchable record build
        write_build(self.build_name)

        result = self.cli('subset', '--target', '10%', '--rest', rest.name, 'gradle',
                          str(self.test_files_dir.joinpath('java/app/src/test/java').resolve()))

        self.assertEqual(result.exit_code, 0)
        self.assertIn("--tests com.launchableinc.rocket_car_gradle.App2Test --tests com.launchableinc.rocket_car_gradle.AppTest --tests com.launchableinc.rocket_car_gradle.utils.UtilsTest", result.output.rstrip('\n'))
        self.assertEqual(rest.read().decode(
        ), '--tests com.launchableinc.rocket_car_gradle.sub.App3Test')
        rest.close()
        os.unlink(rest.name)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset_split(self):
        responses.replace(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(get_base_url(), self.organization, self.workspace), json={
            "testPaths": [[{'type': 'class', 'name': 'com.launchableinc.rocket_car_gradle.App2Test'}], [{'type': 'class', 'name': 'com.launchableinc.rocket_car_gradle.AppTest'}], [{'type': 'class', 'name': 'com.launchableinc.rocket_car_gradle.utils.UtilsTest'}]],
            "rest": [[{'name': 'com.launchableinc.rocket_car_gradle.sub.App3Test'}]],
            "subsettingId": 123,
            "summary": {
                "subset": {"candidates": 3, "duration": 3, "rate": 75},
                "rest": {"candidate": 1, "duration": 1, "rate": 25}
            },
            "isBrainless": False,
        }, status=200)

        # emulate launchable record build
        write_build(self.build_name)

        result = self.cli('subset', '--target', '10%', '--split', 'gradle',
                          str(self.test_files_dir.joinpath('java/app/src/test/java').resolve()))

        self.assertEqual(result.exit_code, 0)
        self.assertIn("subset/123", result.output.rstrip('\n'))

    @ignore_warnings
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_split_subset(self):
        responses.replace(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset/456/slice".format(get_base_url(), self.organization, self.workspace),
                          json={'testPaths': [[{'type': 'class', 'name': 'com.launchableinc.rocket_car_gradle.App2Test'}], [{'type': 'class', 'name': 'com.launchableinc.rocket_car_gradle.AppTest'}], [{'type': 'class', 'name': 'com.launchableinc.rocket_car_gradle.utils.UtilsTest'}]], "rest": [[{'name': 'com.launchableinc.rocket_car_gradle.sub.App3Test'}]]}, status=200)

        rest = tempfile.NamedTemporaryFile(delete=False)
        result = self.cli('split-subset', '--subset-id',
                          'subset/456', '--bin', '1/2', '--rest', rest.name, 'gradle')

        self.assertEqual(result.exit_code, 0)
        self.assertIn("--tests com.launchableinc.rocket_car_gradle.App2Test --tests com.launchableinc.rocket_car_gradle.AppTest --tests com.launchableinc.rocket_car_gradle.utils.UtilsTest", result.output.rstrip('\n'))
        self.assertEqual(rest.read().decode(
        ), '--tests com.launchableinc.rocket_car_gradle.sub.App3Test')
        rest.close()
        os.unlink(rest.name)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_gradle(self):
        result = self.cli('record', 'tests',  '--session', self.session,
                          'gradle', str(self.test_files_dir) + "/**/reports")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[1].request.body).decode())

        expected = self.load_json_from_file(self.result_file_path)
        self.assert_json_orderless_equal(expected, payload)
