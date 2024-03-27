import os
from unittest import mock

import responses  # type: ignore

from tests.cli_test_case import CliTestCase


class GoogleTestTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
        # I use "ctest -N" to get this list.
        pipe = """FooTest.
  Bar
  Baz
  Foo
        """
        result = self.cli('subset', '--target', '10%', '--session', self.session, 'googletest', input=pipe)
        self.assert_success(result)
        self.assert_subset_payload('subset_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test_googletest(self):
        result = self.cli('record', 'tests', '--session', self.session,
                          'googletest', str(self.test_files_dir) + "/")
        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_failed_test_googletest(self):
        # ./test_a --gtest_output=xml:output.xml
        result = self.cli('record', 'tests', '--session', self.session,
                          'googletest', str(self.test_files_dir) + "/fail/")
        self.assert_success(result)
        self.assert_record_tests_payload('fail/record_test_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_empty_dir(self):
        path = 'latest/gtest_*_results.xml'
        result = self.cli('record', 'tests', '--session', self.session,
                          'googletest', path)
        self.assertEqual(result.output.rstrip('\n'), "No matches found: {}".format(path))
        self.assert_success(result)
