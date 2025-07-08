import gzip
import os
import tempfile
from unittest import mock

import responses  # type: ignore

from smart_tests.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class AttachmentTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_attachment(self):
        TEST_CONTENT = b"Hello world"

        # Test requires explicit session parameter

        attachment = tempfile.NamedTemporaryFile(delete=False)
        attachment.write(TEST_CONTENT)
        attachment.close()

        # gimick to capture the payload sent to the server, while the request is in flight
        # the body is a generator, so unless it's consumed within the request, we won't be able to access it
        body = None

        def verify_body(request):
            nonlocal body
            body = gzip.decompress(b''.join(list(request.body)))  # request.body is a generator
            return (200, [], None)

        # Mock session name lookup (needed before attachment upload) - override base class 404
        responses.replace(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/"
            f"{self.workspace}/builds/{self.build_name}/test_session_names/{self.session_name}",
            json={
                'id': self.session_id,
                'isObservation': False,
            },
            status=200)

        responses.add_callback(
            responses.POST,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/"
            f"{self.workspace}/builds/{self.build_name}/test_sessions/{self.session_id}/attachment",
            callback=verify_body)

        result = self.cli("record", "attachment", "--session", self.session_name, "--build", self.build_name, attachment.name)

        self.assert_success(result)
        self.assertEqual(TEST_CONTENT, body)

        os.unlink(attachment.name)
