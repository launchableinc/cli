from pathlib import Path
import responses  # type: ignore
import json
import gzip
from tests.cli_test_case import CliTestCase
from launchable.utils.http_client import get_base_url


class NUnitTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath('../data/nunit/').resolve()

    @responses.activate
    def test_subset(self):
        responses.replace(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(get_base_url(), self.organization, self.workspace),
                          json={'testPaths': [
                              [
                                  {"type": "Assembly", "name": "calc.dll"},
                                  {"type": "TestSuite", "name": "ParameterizedTests"},
                                  {"type": "TestFixture", "name": "MyTests"},
                                  {"type": "ParameterizedMethod", "name": "DivideTest"},
                                  {"type": "TestCase", "name": "DivideTest(12,3)"}
                              ],
                              [
                                  {"type": "Assembly", "name": "calc.dll"},
                                  {"type": "TestSuite", "name": "calc"},
                                  {"type": "TestFixture", "name": "Tests1"},
                                  {"type": "TestCase", "name": "Test1"}
                              ]
                          ]}, status=200)

        result = self.cli('subset', '--target', '10%', '--session', self.session,
                          'nunit', str(self.test_files_dir) + "/list.xml")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[0].request.body).decode())

        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('subset_result.json'))

        self.assert_json_orderless_equal(expected, payload)

        output = 'ParameterizedTests.MyTests.DivideTest(12,3)\ncalc.Tests1.Test1'
        self.assertEqual(result.output.rstrip('\n'), output)

    @responses.activate
    def test_record_test(self):
        result = self.cli('record', 'tests',  '--session', self.session,
                          'nunit', str(self.test_files_dir) + "/output.xml")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            b''.join(responses.calls[1].request.body)).decode())

        expected = self.load_json_from_file(
            self.test_files_dir.joinpath("record_test_result.json"))

        self.assert_json_orderless_equal(expected, payload)
