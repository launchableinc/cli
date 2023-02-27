import gzip
import json
import os
from pathlib import Path
from unittest import mock

import responses  # type: ignore

from launchable.utils.session import read_session, write_build
from tests.cli_test_case import CliTestCase


class ProveTestTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath('../data/prove/').resolve()

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_tests(self):
        # emulate launchable record build
        write_build(self.build_name)

        result = self.cli('record', 'tests', 'prove', str(self.test_files_dir.joinpath('report.xml')))
        self.assertEqual(result.exit_code, 0)

        self.assertEqual(read_session(self.build_name), self.session)

        self.assertIn('events', responses.calls[2].request.url, 'call events API')
        payload = json.loads(gzip.decompress(responses.calls[2].request.body).decode())
        for c in payload['events']:
            del c['created_at']

        expected = self.load_json_from_file(self.test_files_dir.joinpath('record_test_result.json'))
        self.assert_json_orderless_equal(expected, payload)

        self.assertIn('close', responses.calls[4].request.url, 'call close API')
