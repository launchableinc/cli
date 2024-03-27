import os
from pathlib import Path
from unittest import mock

import responses  # type: ignore

from launchable.utils.http_client import get_base_url
from launchable.utils.session import write_build
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
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
        # emulate launchable record build
        write_build(self.build_name)

        result = self.cli('subset', '--target', '10%', '--base',
                          os.getcwd(), 'jest', input=self.subset_input)
        self.assert_success(result)
        self.assert_subset_payload('subset_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    @ignore_warnings
    def test_subset_split(self):
        test_path = Path("{}/components/layouts/modal/snapshot.test.tsx".format(os.getcwd()))
        responses.replace(responses.POST,
                          "{}/intake/organizations/{}/workspaces/{}/subset".format(get_base_url(),
                                                                                   self.organization,
                                                                                   self.workspace),
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

        # emulate launchable record build
        write_build(self.build_name)

        result = self.cli('subset', '--target', '20%', '--base', os.getcwd(), '--split',
                          'jest', input=self.subset_input)

        self.assert_success(result)

        self.assertIn('subset/123', result.output)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test(self):
        # emulate launchable record build
        write_build(self.build_name)

        result = self.cli('record', 'tests', 'jest', str(self.test_files_dir.joinpath("junit.xml")))
        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')
