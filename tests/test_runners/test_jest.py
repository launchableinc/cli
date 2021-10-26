from pathlib import Path
import responses  # type: ignore
import json
import gzip
import os
from pathlib import Path
from unittest import mock
from tests.cli_test_case import CliTestCase
from launchable.utils.http_client import get_base_url
import tempfile
from tests.helper import ignore_warnings


class JestTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath(
        '../data/jest/').resolve()
    # This string generate absolute paths because the CLI requires exsisting directory path
    subset_input = """
> launchable@0.1.0 test
> jest "--listTests"

{}/__tests__/pages/organizations/workspaces/index.test.tsx
{}/components/layouts/modal/snapshot.test.tsx
{}/components/molecules/mobile-sidebar/snapshot.test.tsx
{}/components/atoms/button/index.test.tsx
{}/components/layouts/sidebar/snapshot.test.tsx
{}/components/molecules/sidebar/snapshot.test.tsx
{}/components/atoms/toggle/snapshot.test.tsx
{}/components/layouts/error/snapshot.test.tsx
{}/components/layouts/email-required/snapshot.test.tsx
{}/components/layouts/loading/snapshot.test.tsx
""".format(*(os.getcwd() for _ in range(10)))

    result_file_path = test_files_dir.joinpath('record_test_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
        result = self.cli('subset', '--target', '10%',
                          '--build', self.build_name, '--base', os.getcwd(), 'jest', input=self.subset_input)
        print(result.output)
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[1].request.body).decode())
        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('subset_result.json'))
        self.assert_json_orderless_equal(payload, expected)
