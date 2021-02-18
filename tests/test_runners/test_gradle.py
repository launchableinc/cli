from pathlib import Path
from unittest import mock
import responses # type: ignore
import json
import gzip
from tests.cli_test_case import CliTestCase
from launchable.utils.http_client import get_base_url


class GradleTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath(
        '../data/gradle/').resolve()
    result_file_path = test_files_dir.joinpath('recursion/expected.json')

    @responses.activate
    def test_subset_without_session(self):
        responses.replace(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(get_base_url(), self.organization, self.workspace),
                          json={'testPaths': [[{'name': 'com.launchableinc.rocket_car_gradle.AppTest2'}], [{'name': 'com.launchableinc.rocket_car_gradle.AppTest'}], [{'name': 'com.launchableinc.rocket_car_gradle.sub.AppTest3'}], [{'name': 'com.launchableinc.rocket_car_gradle.utils.UtilsTest'}]]}, status=200)
        result = self.cli('subset', '--target', '10%', '--build',
                          self.build_name, 'gradle', str(self.test_files_dir.joinpath('java/app/test').resolve()))
        self.assertEqual(result.exit_code, 0)
        output = '--tests com.launchableinc.rocket_car_gradle.AppTest2 --tests com.launchableinc.rocket_car_gradle.AppTest --tests com.launchableinc.rocket_car_gradle.sub.AppTest3 --tests com.launchableinc.rocket_car_gradle.utils.UtilsTest'
        self.assertEqual(result.output.rstrip('\n'), output)

    @responses.activate
    def test_record_test_gradle(self):
        result = self.cli('record', 'tests',  '--session', self.session,
                          'gradle', str(self.test_files_dir) + "/**/reports")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            b''.join(responses.calls[0].request.body)).decode())

        expected = self.load_json_from_file(self.result_file_path)
        self.assert_json_orderless_equal(expected, payload)
