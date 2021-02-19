from pathlib import Path
import responses # type: ignore
import json
import gzip
from tests.cli_test_case import CliTestCase


class GoogleTestTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath(
        '../data/googletest/').resolve()

    @responses.activate
    def test_subset(self):
        # I use "ctest -N" to get this list.
        pipe = """FooTest.
  Bar
  Baz
  Foo
        """
        result = self.cli('subset', '--target', '10%',
                          '--session', self.session, 'googletest', input=pipe)
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[0].request.body).decode())
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('subset_result.json'))
        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    def test_record_test_googletest(self):
        result = self.cli('record', 'tests',  '--session', self.session,
                          'googletest', str(self.test_files_dir) + "/")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            b''.join(responses.calls[0].request.body)).decode())
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('record_test_result.json'))

        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    def test_record_failed_test_googletest(self):
        # ./test_a --gtest_output=xml:output.xml
        result = self.cli('record', 'tests',  '--session', self.session,
                          'googletest', str(self.test_files_dir) + "/fail/")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            b''.join(responses.calls[0].request.body)).decode())
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('fail/record_test_result.json'))

        self.assert_json_orderless_equal(expected, payload)

    @responses.activate
    def test_record_empty_dir(self):
        path = 'latest/gtest_*_results.xml'
        result = self.cli('record', 'tests',  '--session', self.session,
                          'googletest', path)
        self.assertEqual(result.output.rstrip(
            '\n'), "No matches found: {}".format(path))
        self.assertEqual(result.exit_code, 0)
