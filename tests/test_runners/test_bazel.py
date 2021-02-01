from pathlib import Path
import responses
import json
import gzip
from launchable.utils.session import read_session
from tests.cli_test_case import CliTestCase


class BazelTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath(
        '../data/bazel/').resolve()

    @responses.activate
    def test_subset(self):
        pipe = """Starting local Bazel server and connecting to it...
//src/test/java/com/ninjinkun:mylib_test9
//src/test/java/com/ninjinkun:mylib_test8
//src/test/java/com/ninjinkun:mylib_test7
//src/test/java/com/ninjinkun:mylib_test6
//src/test/java/com/ninjinkun:mylib_test5
//src/test/java/com/ninjinkun:mylib_test4
//src/test/java/com/ninjinkun:mylib_test3
//src/test/java/com/ninjinkun:mylib_test2
//src/test/java/com/ninjinkun:mylib_test1
Loading: 2 packages loaded
"""
        result = self.cli('subset', '--target', '10%',
                          '--build', self.build_name, 'bazel', input=pipe)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(read_session(self.build_name), self.session)

        payload = json.loads(gzip.decompress(
            responses.calls[1].request.body).decode())
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('subset_result.json'))
        self.assertEqual(payload, expected)

    def test_record_test(self):
        pass
