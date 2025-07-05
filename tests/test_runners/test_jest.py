import os
from pathlib import Path
from unittest import mock

import responses  # type: ignore

from smart_tests.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase
from tests.helper import ignore_warnings


class JestTest(CliTestCase):
    # This string generate absolute paths because the CLI requires exsisting
    # directory path
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

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_subset(self):
        result = self.cli(
            'subset',
            'jest',
            '--session',
            self.session_name,
            '--build',
            self.build_name,
            '--target',
            '10%',
            '--base',
            os.getcwd(),
            input=self.subset_input)
        self.assert_success(result)
        self.assert_subset_payload('subset_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    @ignore_warnings
    def test_subset_split(self):
        test_path = Path(f"{os.getcwd()}/components/layouts/modal/snapshot.test.tsx")
        responses.replace(responses.POST,
                          f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/{self.workspace}/subset",
                          json={'testPaths': [[{'name': str(test_path)}]],
                                'rest': [],
                                'subsettingId': 123,
                                'summary': {'subset': {'duration': 10,
                                                       'candidates': 1,
                                                       'rate': 100},
                                            'rest': {'duration': 0,
                                                     'candidates': 0,
                                                     'rate': 0}},
                                "isBrainless": False,
                                },
                          status=200)
        result = self.cli('subset', 'jest', '--session', self.session_name, '--build', self.build_name,
                          '--target', '20%', '--base', os.getcwd(), '--split', input=self.subset_input)

        self.assert_success(result)

        self.assertIn('subset/123', result.output)

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_test(self):
        result = self.cli('record', 'test', 'jest', '--session', self.session_name, '--build', self.build_name,
                          str(self.test_files_dir.joinpath('junit.xml')))
        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')
