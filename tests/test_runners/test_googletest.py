from pathlib import Path
from unittest import mock

from tests.cli_test_case import CliTestCase


class GoogleTestTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath(
        '../data/googletest/').resolve()

    @mock.patch('requests.request')
    def test_subset(self, mock_post):
        # I use "ctest -N" to get this list.
        pipe = "Test project github.com/launchableinc/rocket-car-googletest\n  Test #1: FooTest.Bar\n  Test #2: FooTest.Baz\n  Test #3: FooTest.Foo\n  Test #4: */ParameterizedTest.Bar/*\n\nTotal Tests: 4"
        result = self.cli('subset', '--target', '10%',
                          '--session', self.session, 'googletest', input=pipe)
        self.assertEqual(result.exit_code, 0)

        payload = self.gzipped_json_payload(mock_post)
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('subset_result.json'))
        self.assert_json_orderless_equal(expected, payload)

    @mock.patch('requests.request')
    def test_record_test_googletest(self, mock_post):
        result = self.cli('record', 'tests',  '--session', self.session,
                          'googletest', str(self.test_files_dir) + "/")
        self.assertEqual(result.exit_code, 0)

        payload = self.gzipped_json_payload(mock_post)
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('record_test_result.json'))

        self.assert_json_orderless_equal(expected, payload)
