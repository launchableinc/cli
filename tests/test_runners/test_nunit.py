from pathlib import Path
import responses  # type: ignore
import json
import gzip
import os
from tests.cli_test_case import CliTestCase
from launchable.utils.http_client import get_base_url
from unittest import mock
import tempfile
from tests.helper import ignore_warnings


class NUnitTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath('../data/nunit/').resolve()

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
        responses.replace(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(get_base_url(), self.organization, self.workspace),
                          json={'testPaths': [
                              [
                                  {"type": "Assembly", "name": "calc.dll"},
                                  {"type": "TestSuite", "name": "ParameterizedTests"},
                                  {"type": "TestFixture", "name": "MyTests"},
                                  {"type": "ParameterizedMethod",
                                      "name": "DivideTest"},
                                  {"type": "TestCase",
                                      "name": "DivideTest(12,3)"}
                              ],
                              [
                                  {"type": "Assembly", "name": "calc.dll"},
                                  {"type": "TestSuite", "name": "calc"},
                                  {"type": "TestFixture", "name": "Tests1"},
                                  {"type": "TestCase", "name": "Test1"}
                              ]
                          ],
            'rest': [],
            'subsettingId': 123,
            'summary': {
                'subset': {'duration': 15, 'candidates': 2, 'rate': 100},
                'rest': {'duration': 0, 'candidates': 0, 'rate': 0}
                          },
        }, status=200)

        result = self.cli('subset', '--target', '10%', '--session', self.session,
                          'nunit', str(self.test_files_dir) + "/list.xml")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[0].request.body).decode())

        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('subset_result.json'))

        self.assert_json_orderless_equal(expected, payload)

        output = 'ParameterizedTests.MyTests.DivideTest(12,3)\ncalc.Tests1.Test1'
        self.assertIn(output, result.output)

    @ignore_warnings
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_split_subset(self):
        responses.replace(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset/456/slice".format(get_base_url(), self.organization, self.workspace),
                          json={
                              'testPaths': [
                                  [
                                      {"type": "Assembly", "name": "calc.dll"},
                                      {"type": "TestSuite",
                                          "name": "ParameterizedTests"},
                                      {"type": "TestFixture", "name": "MyTests"},
                                      {"type": "ParameterizedMethod",
                                       "name": "DivideTest"},
                                      {"type": "TestCase",
                                       "name": "DivideTest(12,3)"}
                                  ]
                              ],
            'rest': [[
                {"type": "Assembly", "name": "calc.dll"},
                {"type": "TestSuite", "name": "calc"},
                {"type": "TestFixture", "name": "Tests1"},
                {"type": "TestCase", "name": "Test1"}
            ]],
            'subsettingId': 456,
            'summary': {
                'subset': {'duration': 8, 'candidates': 1, 'rate': 50},
                'rest': {'duration': 7, 'candidates': 1, 'rate': 50}
                              },
        }, status=200)

        rest = tempfile.NamedTemporaryFile(delete=False)
        result = self.cli('split-subset', '--subset-id', 'subset/456',
                          '--bin', '1/2', '--rest', rest.name, 'nunit')

        self.assertEqual(result.exit_code, 0)

        self.assertIn('ParameterizedTests.MyTests.DivideTest(12,3)',
                      result.output)

        self.assertEqual(rest.read().decode(), 'calc.Tests1.Test1')
        rest.close()
        os.unlink(rest.name)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_on_linux(self):
        result = self.cli('record', 'tests',  '--session', self.session,
                          'nunit', str(self.test_files_dir) + "/output-linux.xml")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[1].request.body).decode())

        expected = self.load_json_from_file(
            self.test_files_dir.joinpath("record_test_result.json"))

        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_on_windows(self):
        result = self.cli('record', 'tests',  '--session', self.session,
                          'nunit', str(self.test_files_dir) + "/output-windows.xml")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[1].request.body).decode())

        expected = self.load_json_from_file(
            self.test_files_dir.joinpath("record_test_result.json"))

        self.assert_json_orderless_equal(expected, payload)
