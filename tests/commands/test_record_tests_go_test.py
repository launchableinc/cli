from unittest import TestCase, mock
from nose.tools import eq_, ok_
from click.testing import CliRunner
from test.support import captured_stdin

import os
import json
from pathlib import Path
import gzip

from launchable.__main__ import main


class GoTestTest(TestCase):
    launchable_token = 'v1:launchableinc/mothership:auth-token-sample'
    session = '/intake/organizations/launchableinc/workspaces/mothership/builds/123/test_sessions/16'
    test_files_dir = Path(__file__).parent.joinpath(
        '../data/go_test/').resolve()

    def setUp(self):
        self.maxDiff = None
        os.environ['LAUNCHABLE_TOKEN'] = self.launchable_token

    @mock.patch('requests.request')
    def test_subset(self, mock_post):
        runner = CliRunner()
        pipe = "TestExample1\nTestExample2\nTestExample3\nTestExample4\nok      github.com/launchableinc/rocket-car-gotest      0.268s"
        result = runner.invoke(main, [
                               'subset', '--target', '10%', '--session', self.session, 'go_test'], input=pipe)

        self.assertEqual(result.exit_code, 0)

        for (args, kwargs) in mock_post.call_args_list:
            if kwargs['data']:
                data = kwargs['data']

        result_file_path = self.test_files_dir.joinpath('subset_result.json')
        with result_file_path.open() as json_file:
            expected = json.load(json_file)
            self.assertDictEqual(json.loads(data.decode()), expected)

    @mock.patch('requests.request')
    def test_record_tests(self, mock_post):
        runner = CliRunner()
        result = runner.invoke(main, ['record', 'tests',  '--session',
                                      self.session, 'go_test', str(self.test_files_dir) + "/"])
        self.assertEqual(result.exit_code, 0)

        for (args, kwargs) in mock_post.call_args_list:
            if kwargs['data']:
                data = kwargs['data']
        zipped_payload = b''.join(data)
        payload = json.loads(gzip.decompress(zipped_payload).decode())

        result_file_path = self.test_files_dir.joinpath(
            'record_test_result.json')
        with result_file_path.open() as json_file:
            expected = json.load(json_file)

            # Normalize events order that depends on shell glob implementation
            payload['events'] = sorted(
                payload['events'], key=lambda c: c['testPath'][0]['name'])
            expected['events'] = sorted(
                expected['events'], key=lambda c: c['testPath'][0]['name'])

            # Remove timestamp because it depends on the machine clock
            for c in payload['events']:
                del c['created_at']
            for c in expected['events']:
                del c['created_at']

            self.assertDictEqual(payload, expected)
