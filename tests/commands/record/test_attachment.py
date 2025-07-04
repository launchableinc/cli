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

        responses.add_callback(
            responses.POST,
            "{}/intake/organizations/{}/workspaces/{}/builds/{}/test_sessions/{}/attachment".format(
                get_base_url(), self.organization, self.workspace, self.build_name, self.session_id),
            callback=verify_body)

        result = self.cli("record", "attachment", "--session", self.session_name, "--build", self.build_name, attachment.name)

        self.assert_success(result)
        self.assertEqual(TEST_CONTENT, body)

        os.unlink(attachment.name)
