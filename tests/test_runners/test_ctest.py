from pathlib import Path
import responses
import json
import gzip
from launchable.utils.session import read_session
from tests.cli_test_case import CliTestCase


class CTestTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath(
        '../data/ctest/').resolve()
    subset_input = """Test project /Users/ninjin/src/github.com/launchable/rocket-car-ctest/build
  Test  #1: TestScreenshotGallery
  Test  #2: TestUtilities
  Test  #3: TestDirectedAcyclicGraph
  Test  #4: TestTime

Total Tests: 4
"""

    @responses.activate
    def test_subset_without_session(self):
        result = self.cli('subset', '--target', '10%', '--build',
                          self.build_name, 'ctest', input=self.subset_input)
        print(result.output)
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[1].request.body).decode())
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('subset_result.json'))
        self.assert_json_orderless_equal(payload, expected)

    @responses.activate
    def test_record_test(self):
        print(str(self.test_files_dir) + "/Testing")
        result = self.cli('record', 'tests', '--build',
                          self.build_name, 'ctest', str(self.test_files_dir) + "/Testing/20210129-0917")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(read_session(self.build_name), self.session)
        print(result.output)

        payload = json.loads(gzip.decompress(
            b''.join(responses.calls[1].request.body)).decode())
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('record_test_result.json'))

        for c in payload['events']:
            del c['created_at']

        self.assert_json_orderless_equal(payload, expected)