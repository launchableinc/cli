import gzip
import json
import os
from unittest import mock

import responses  # type: ignore

from launchable.test_runners.pytest import _parse_pytest_nodeid
from tests.cli_test_case import CliTestCase


class PytestTest(CliTestCase):
    subset_input = '''tests/funcs3_test.py::test_func4
tests/funcs3_test.py::test_func5
tests/test_funcs1.py::test_func1
tests/test_funcs1.py::test_func2
tests/test_funcs2.py::test_func3
tests/test_funcs2.py::test_func4
tests/test_mod.py::TestClass::test__can_print_aaa
tests/fooo/func4_test.py::test_func6
tests/fooo/filenameonly_test.py

9 tests collected in 0.02s
'''

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
        result = self.cli('subset', '--target', '10%', '--session',
                          self.session, 'pytest', input=self.subset_input)
        self.assert_success(result)

        payload = json.loads(gzip.decompress(self.find_request('/subset').request.body).decode())
        expected = self.load_json_from_file(self.test_files_dir.joinpath('subset_result.json'))
        for test_path in expected["testPaths"]:
            test_path[0]['name'] = os.path.normpath(test_path[0]['name'])
        self.assertEqual(expected, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_pytest(self):
        result = self.cli('record', 'tests', '--session', self.session,
                          'pytest', str(self.test_files_dir.joinpath("report.xml")))

        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_with_json_option(self):
        result = self.cli('record', 'tests', '--session', self.session,
                          'pytest', '--json', str(self.test_files_dir.joinpath("report.json")))

        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result_json.json')

    def setUp(self):
        super().setUp()
        self.current_dir = os.getcwd()
        os.chdir(str(self.test_files_dir))

    def tearDown(self):
        os.chdir(self.current_dir)
        super().tearDown()

    def test_parse_pytest_nodeid(self):

        self.assertEqual(_parse_pytest_nodeid("tests/test_mod.py::TestClass::test__can_print_aaa"), [
            {"type": "file", "name": os.path.normpath("tests/test_mod.py")},
            {"type": "class", "name": "tests.test_mod.TestClass"},
            {"type": "testcase", "name": "test__can_print_aaa"},
        ])

        self.assertEqual(_parse_pytest_nodeid("tests/fooo/func4_test.py::test_func6"), [
            {"type": "file", "name": os.path.normpath(
                "tests/fooo/func4_test.py")},
            {"type": "class", "name": "tests.fooo.func4_test"},
            {"type": "testcase", "name": "test_func6"},
        ])
