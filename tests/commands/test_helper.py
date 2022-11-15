
import os
from io import StringIO
from unittest import mock

import responses  # type: ignore

from launchable.commands.helper import _check_observation_mode_status
from launchable.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class HelperTest(CliTestCase):

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_check_observation_mode_status(self):
        test_session = "builds/{}/test_sessions/{}".format(
            self.build_name,
            self.session_id,
        )

        with mock.patch('sys.stderr', new=StringIO()) as stderr:
            _check_observation_mode_status(test_session, False)
            print(stderr.getvalue())
            self.assertNotIn("WARNING:", stderr.getvalue())

        request_path = "{}/intake/organizations/{}/workspaces/{}/{}".format(
            get_base_url(),
            self.organization,
            self.workspace,
            test_session,
        )

        with mock.patch('sys.stderr', new=StringIO()) as stderr:
            responses.replace(
                responses.GET,
                request_path,
                json={
                    "isObservation": False
                }, status=200)

            _check_observation_mode_status(test_session, True)
            self.assertIn("WARNING:", stderr.getvalue())

        with mock.patch('sys.stderr', new=StringIO()) as stderr:
            responses.replace(
                responses.GET,
                request_path,
                json={
                    "isObservation": True
                }, status=200)

            _check_observation_mode_status(test_session, True)
            self.assertNotIn("WARNING:", stderr.getvalue())

        with mock.patch('sys.stderr', new=StringIO()) as stderr:
            responses.replace(
                responses.GET,
                request_path,
                json={
                    "isObservation": True
                }, status=404)

            _check_observation_mode_status(test_session, False)

            # not check when status isn't 200
            self.assertNotIn("WARNING:", stderr.getvalue())
