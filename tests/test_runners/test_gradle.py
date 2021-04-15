from pathlib import Path
from unittest import mock
import responses  # type: ignore
import json
import gzip
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
    def test_subset_without_session(self):
        responses.replace(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(get_base_url(), self.organization, self.workspace),
                          json={'testPaths': [[{'name': 'com.launchableinc.rocket_car_gradle.App2Test'}], [{'name': 'com.launchableinc.rocket_car_gradle.AppTest'}], [{'name': 'com.launchableinc.rocket_car_gradle.sub.App3Test'}], [{'name': 'com.launchableinc.rocket_car_gradle.utils.UtilsTest'}]]}, status=200)
        result = self.cli('subset', '--target', '10%', '--build',
                          self.build_name, 'gradle', str(self.test_files_dir.joinpath('java/app/test').resolve()))
        self.assertEqual(result.exit_code, 0)
        output = '--tests com.launchableinc.rocket_car_gradle.App2Test --tests com.launchableinc.rocket_car_gradle.AppTest --tests com.launchableinc.rocket_car_gradle.sub.App3Test --tests com.launchableinc.rocket_car_gradle.utils.UtilsTest'
        self.assertEqual(result.output.rstrip('\n'), output)

    @ignore_warnings
    @responses.activate
    def test_subset_rest(self):
        responses.replace(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(get_base_url(), self.organization, self.workspace),
                          json={'testPaths': [[{'type': 'class', 'name': 'com.launchableinc.rocket_car_gradle.App2Test'}], [{'type': 'class', 'name': 'com.launchableinc.rocket_car_gradle.AppTest'}], [{'type': 'class', 'name': 'com.launchableinc.rocket_car_gradle.utils.UtilsTest'}]]}, status=200)

        rest = tempfile.NamedTemporaryFile(delete=False)
        result = self.cli('subset', '--target', '10%', '--build',
                          self.build_name, '--rest', rest.name, 'gradle', str(self.test_files_dir.joinpath('java/app/src/test/java').resolve()))

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output.rstrip(
            '\n'), "--tests com.launchableinc.rocket_car_gradle.App2Test --tests com.launchableinc.rocket_car_gradle.AppTest --tests com.launchableinc.rocket_car_gradle.utils.UtilsTest")
        self.assertEqual(rest.read().decode(
        ), '--tests com.launchableinc.rocket_car_gradle.sub.App3Test')
        rest.close()
        os.unlink(rest.name)

    @responses.activate
    def test_record_test_gradle(self):
        result = self.cli('record', 'tests',  '--session', self.session,
                          'gradle', str(self.test_files_dir) + "/**/reports")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            b''.join(responses.calls[0].request.body)).decode())

        expected = self.load_json_from_file(self.result_file_path)
        self.assert_json_orderless_equal(expected, payload)
