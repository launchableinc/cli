from pathlib import Path
from unittest import mock
import responses  # type: ignore
import json
import gzip
import os
from tests.cli_test_case import CliTestCase


class RobotTest(CliTestCase):
    test_files_dir = Path(__file__).parent.joinpath(
        '../data/robot/').resolve()

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
        result = self.cli('subset', '--target', '10%', '--session',
                          self.session, 'robot', str(self.test_files_dir) + "/dryrun.xml")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[0].request.body).decode())

        expected = self.load_json_from_file(
            self.test_files_dir.joinpath('subset_result.json'))

        self.assert_json_orderless_equal(expected, payload)

    @ responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test(self):

        result = self.cli('record', 'tests',  '--session', self.session,
                          'robot', str(self.test_files_dir) + "/output.xml")
        self.assertEqual(result.exit_code, 0)

        payload = json.loads(gzip.decompress(
            responses.calls[1].request.body).decode())

        for e in payload["events"]:
            del e["created_at"]

        expected = self.load_json_from_file(
            self.test_files_dir.joinpath("record_test_result.json"))

        self.assert_json_orderless_equal(expected, payload)
