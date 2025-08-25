
import os
from io import StringIO
from unittest import mock

import responses  # type: ignore

from smart_tests.commands.helper import _check_observation_mode_status
from smart_tests.utils.commands import Command
from smart_tests.utils.http_client import get_base_url
from smart_tests.utils.tracking import TrackingClient
from tests.cli_test_case import CliTestCase


class HelperTest(CliTestCase):

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_check_observation_mode_status(self):
        test_session = f"builds/{self.build_name}/test_sessions/{self.session_id}"

        tracking_client = TrackingClient(Command.RECORD_TESTS)

        with mock.patch('sys.stderr', new=StringIO()) as stderr:
            _check_observation_mode_status(test_session, False, tracking_client=tracking_client)
            print(stderr.getvalue())
            self.assertNotIn("WARNING:", stderr.getvalue())

        request_path = f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/{self.workspace}/{test_session}"

        with mock.patch('sys.stderr', new=StringIO()) as stderr:
            responses.replace(
                responses.GET,
                request_path,
                json={
                    "isObservation": False
                }, status=200)

            _check_observation_mode_status(test_session, True, tracking_client=tracking_client)
            self.assertIn("WARNING:", stderr.getvalue())

        with mock.patch('sys.stderr', new=StringIO()) as stderr:
            responses.replace(
                responses.GET,
                request_path,
                json={
                    "isObservation": True
                }, status=200)

            _check_observation_mode_status(test_session, True, tracking_client=tracking_client)
            self.assertNotIn("WARNING:", stderr.getvalue())

        with mock.patch('sys.stderr', new=StringIO()) as stderr:
            responses.replace(
                responses.GET,
                request_path,
                json={
                    "isObservation": True
                }, status=404)

            _check_observation_mode_status(test_session, False, tracking_client=tracking_client)

            # not check when status isn't 200
            self.assertNotIn("WARNING:", stderr.getvalue())
