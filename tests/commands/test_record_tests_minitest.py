from unittest import TestCase, mock
from nose.tools import eq_, ok_
from click.testing import CliRunner

import os
import json
from pathlib import Path
import gzip

from launchable.__main__ import main
from launchable.utils.gzipgen import compress

class MinitestTest(TestCase):
    launchable_token='v1:launchableinc/mothership:auth-token-sample'
    session = '/intake/organizations/launchableinc/workspaces/mothership/builds/123/test_sessions/16'
    test_files_dir = Path(__file__).parent.joinpath('../data/minitest/').resolve()
    result_file_path = test_files_dir.joinpath('record_test_result.json')

    def setUp(self):
        os.environ['LAUNCHABLE_TOKEN'] = self.launchable_token

    @mock.patch('requests.request')
    def test_record_test_minitest(self, mock_post):
        runner = CliRunner()
        result = runner.invoke(main, ['record', 'tests',  '--session', self.session, 'minitest', str(self.test_files_dir) + "/"])
        eq_(result.exit_code, 0)

        zipped_payload = b''.join(mock_post.call_args.kwargs['data'])
        payload = json.loads(gzip.decompress(zipped_payload).decode())
        with self.result_file_path.open() as json_file:
            expected = json.load(json_file)
            self.assertDictEqual(payload, expected)
