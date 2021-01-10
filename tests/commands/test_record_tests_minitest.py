from unittest import TestCase, mock
from nose.tools import eq_, ok_
from click.testing import CliRunner

import os
import json
from pathlib import Path

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
        # TODO: uncompress data, then compare them as Python object
        zipped_payload = b''.join(mock_post.call_args.kwargs['data'])

        with self.result_file_path.open() as json_file:
            json_obj = json.load(json_file)
            # TODO: remove compress method
            eq_(zipped_payload, b''.join(compress((json.dumps(json_obj).encode(),))))
