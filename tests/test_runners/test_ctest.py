from pathlib import Path
import responses  # type: ignore
import json
import gzip
from launchable.utils.session import read_session
from tests.cli_test_case import CliTestCase
import tempfile


class CTestTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath(
        '../data/ctest/').resolve()

    @responses.activate
    def test_subset_without_session(self):
        result = self.cli('subset', '--target', '10%', '--build',
                          self.build_name, 'ctest', str(self.test_files_dir.joinpath("ctest_list.json")))
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[1].request.body).decode())
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('subset_result.json'))
        self.assert_json_orderless_equal(payload, expected)

    def test_subset_diff(self):
        tf = tempfile.NamedTemporaryFile()
        tf.write(b'''^FooTest.Bar$
^*/ParameterizedTest.Bar/*$''')
        tf.seek(0)

        result = self.cli('subset', '--diff', tf.name, 'ctest',
                          str(self.test_files_dir.joinpath("ctest_list.json")))
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, '''^FooTest.Baz$
^FooTest.Foo$
''')

    @responses.activate
    def test_record_test(self):
        result = self.cli('record', 'tests', '--build',
                          self.build_name, 'ctest', str(self.test_files_dir) + "/Testing/**/Test.xml")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(read_session(self.build_name), self.session)

        payload = json.loads(gzip.decompress(
            b''.join(responses.calls[1].request.body)).decode())
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('record_test_result.json'))

        for c in payload['events']:
            del c['created_at']
        self.assert_json_orderless_equal(payload, expected)
