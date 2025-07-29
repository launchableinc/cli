import gzip
import os
import tempfile
from unittest import mock

import responses  # type: ignore

from smart_tests.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase
from tests.helper import ignore_warnings


class GradleTest(CliTestCase):
    @ignore_warnings
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

        responses.replace(
            responses.POST,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/{self.workspace}/subset",
            json={
                "testPaths": [
                    [{'name': 'com.launchableinc.rocket_car_gradle.App2Test'}],
                    [{'name': 'com.launchableinc.rocket_car_gradle.AppTest'}],
                    [{'name': 'com.launchableinc.rocket_car_gradle.sub.App3Test'}],
                    [{'name': 'com.launchableinc.rocket_car_gradle.utils.UtilsTest'}]
                ],
                "rest": [],
                "subsettingId": 456,
                "summary": {
                    "subset": {"candidates": 4, "duration": 4, "rate": 100},
                    "rest": {"candidate": 0, "duration": 0, "rate": 0},
                },
                "isBrainless": False},
            status=200)
        result = self.cli('subset', 'gradle', '--session', self.session_name, '--build', self.build_name, '--target', '10%',
                          str(self.test_files_dir.joinpath('java/app/src/test').resolve()))
        # TODO: we need to assert on the request payload to make sure it found
        # test list all right
        self.assert_success(result)

        output = "--tests com.launchableinc.rocket_car_gradle.App2Test " \
                 "--tests com.launchableinc.rocket_car_gradle.AppTest " \
                 "--tests com.launchableinc.rocket_car_gradle.sub.App3Test " \
                 "--tests com.launchableinc.rocket_car_gradle.utils.UtilsTest"
        self.assertIn(output, result.output.rstrip('\n'))

    @ignore_warnings
    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_subset_rest(self):
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
                    [{'type': 'class',
                      'name': 'com.launchableinc.rocket_car_gradle.App2Test'}],
                    [{'type': 'class',
                      'name': 'com.launchableinc.rocket_car_gradle.AppTest'}],
                    [{'type': 'class',
                      'name': 'com.launchableinc.rocket_car_gradle.utils.UtilsTest'}],
                ],
                "rest": [[{'name': 'com.launchableinc.rocket_car_gradle.sub.App3Test'}]],
                "subsettingId": 456,
                "summary": {
                    "subset": {"candidates": 3, "duration": 3, "rate": 75},
                    "rest": {"candidate": 1, "duration": 1, "rate": 25},
                },
                "isBrainless": False,
            },
            status=200)

        rest = tempfile.NamedTemporaryFile(delete=False)
        result = self.cli('subset', 'gradle', '--session', self.session_name, '--build', self.build_name, '--target',
                          '10%', '--rest', rest.name, str(self.test_files_dir.joinpath('java/app/src/test/java').resolve()))

        self.assert_success(result)

        self.assertIn("--tests com.launchableinc.rocket_car_gradle.App2Test "
                      "--tests com.launchableinc.rocket_car_gradle.AppTest "
                      "--tests com.launchableinc.rocket_car_gradle.utils.UtilsTest",
                      result.output.rstrip('\n'))
        self.assertEqual(rest.read().decode(), '--tests com.launchableinc.rocket_car_gradle.sub.App3Test')
        rest.close()
        os.unlink(rest.name)

    @ignore_warnings
    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_subset_zero_input_subsetting(self):
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
                    [{'type': 'class',
                      'name': 'com.launchableinc.rocket_car_gradle.AppTest'}],
                    [{'type': 'class',
                      'name': 'com.launchableinc.rocket_car_gradle.utils.UtilsTest'}],
                ],
                "rest": [
                    [{'name': 'com.launchableinc.rocket_car_gradle.sub.App2Test'}],
                    [{'name': 'com.launchableinc.rocket_car_gradle.sub.App3Test'}],
                ],
                "subsettingId": 456,
                "summary": {
                    "subset": {"candidates": 3, "duration": 3, "rate": 75},
                    "rest": {"candidate": 1, "duration": 1, "rate": 25}
                },
                "isBrainless": False,
            },
            status=200)
        result = self.cli('subset', 'gradle', '--session', self.session_name, '--build', self.build_name, '--target',
                          '10%',
                          '--get-tests-from-previous-sessions',
                          '--output-exclusion-rules',
                          mix_stderr=False)

        if result.exit_code != 0:
            self.assertEqual(
                result.exit_code,
                0,
                "Exit code is not 0. The output is\n" + result.output + "\n" + result.stderr)
        subset_arg = result.output.rstrip('\n')
        self.assertEqual(
            subset_arg,
            "-PexcludeTests=com/launchableinc/rocket_car_gradle/sub/App2Test.class,com/launchableinc/rocket_car_gradle/"
            "sub/App3Test.class")

    @ignore_warnings
    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_subset_zero_input_subsetting_observation(self):
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
                    [{'type': 'class',
                      'name': 'com.launchableinc.rocket_car_gradle.AppTest'}],
                    [{'type': 'class',
                      'name': 'com.launchableinc.rocket_car_gradle.utils.UtilsTest'}],
                ],
                "rest": [
                    [{'name': 'com.launchableinc.rocket_car_gradle.sub.App2Test'}],
                    [{'name': 'com.launchableinc.rocket_car_gradle.sub.App3Test'}],
                ],
                "subsettingId": 456,
                "summary": {
                    "subset": {"candidates": 2, "duration": 3, "rate": 75},
                    "rest": {"candidate": 2, "duration": 1, "rate": 25}
                },
                "isBrainless": False,
                "isObservation": True,
            },
            status=200)
        result = self.cli('subset', 'gradle', '--session', self.session_name, '--build', self.build_name, '--target',
                          '10%',
                          '--get-tests-from-previous-sessions',
                          '--output-exclusion-rules',
                          mix_stderr=False)

        if result.exit_code != 0:
            self.assertEqual(
                result.exit_code,
                0,
                "Exit code is not 0. The output is\n" + result.output + "\n" + result.stderr)
        subset_arg = result.output.rstrip('\n')
        self.assertEqual(subset_arg, "-PexcludeTests=")

    @ignore_warnings
    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_subset_zero_input_subsetting_source_root(self):
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
                    [{'type': 'class',
                      'name': 'com.launchableinc.rocket_car_gradle.AppTest'}],
                    [{'type': 'class',
                      'name': 'com.launchableinc.rocket_car_gradle.utils.UtilsTest'}],
                ],
                "rest": [
                    [{'name': 'com.launchableinc.rocket_car_gradle.sub.App2Test'}],
                    [{'name': 'com.launchableinc.rocket_car_gradle.sub.App3Test'}],
                ],
                "subsettingId": 456,
                "summary": {
                    "subset": {"candidates": 2, "duration": 3, "rate": 75},
                    "rest": {"candidate": 2, "duration": 1, "rate": 25}
                },
                "isBrainless": False,
                "isObservation": True,
            },
            status=200)
        result = self.cli('subset', 'gradle', '--session', self.session_name, '--build', self.build_name, '--target',
                          '10%',
                          '--get-tests-from-previous-sessions',
                          '--output-exclusion-rules',
                          str(self.test_files_dir.joinpath('java/app/src/test').resolve()),
                          mix_stderr=False)

        if result.exit_code != 0:
            self.assertEqual(
                result.exit_code,
                0,
                "Exit code is not 0. The output is\n" + result.output + "\n" + result.stderr)

        body = gzip.decompress(self.find_request('/subset').request.body).decode('utf8')
        self.assertNotIn("java.com.launchableinc.rocket_car_gradle.App2Test", body)

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_subset_split(self):
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
                    [{'type': 'class',
                      'name': 'com.launchableinc.rocket_car_gradle.App2Test'}],
                    [{'type': 'class',
                      'name': 'com.launchableinc.rocket_car_gradle.AppTest'}],
                    [{'type': 'class',
                      'name': 'com.launchableinc.rocket_car_gradle.utils.UtilsTest'}],
                ],
                "rest": [[{'name': 'com.launchableinc.rocket_car_gradle.sub.App3Test'}]],
                "subsettingId": 123,
                "summary": {
                    "subset": {"candidates": 3, "duration": 3, "rate": 75},
                    "rest": {"candidate": 1, "duration": 1, "rate": 25}
                },
                "isBrainless": False,
            },
            status=200)
        result = self.cli('subset', 'gradle', '--session', self.session_name, '--build', self.build_name, '--target',
                          '10%',
                          '--split',
                          str(self.test_files_dir.joinpath('java/app/src/test/java').resolve()))

        self.assert_success(result)

        self.assertIn("subset/123", result.output.rstrip('\n'))

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_test_gradle(self):
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

        result = self.cli('record', 'test', 'gradle', '--build', self.build_name, '--session', self.session_name,
                          str(self.test_files_dir) + "/**/reports")
        self.assert_success(result)
        self.assert_record_tests_payload('recursion/expected.json')
