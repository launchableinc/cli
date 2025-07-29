import os
from unittest import mock

import responses  # type: ignore

from smart_tests.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class XCTestTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ,
                     {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_test(self):
        # Override session name lookup to allow session resolution
        responses.replace(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/"
            f"{self.workspace}/builds/{self.build_name}/test_session_names/{self.session_name}",
            json={
                'id': self.session_id,
                'isObservation': False,
            },
            status=200)

        result = self.cli('record', 'test', 'xctest', '--session', self.session_name, '--build', self.build_name,
                          str(self.test_files_dir.joinpath("junit.xml")))

        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')

    @responses.activate
    @mock.patch.dict(os.environ,
                     {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_subset(self):
        # Override session name lookup to allow session resolution
        responses.replace(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/"
            f"{self.workspace}/builds/{self.build_name}/test_session_names/{self.session_name}",
            json={
                'id': self.session_id,
                'isObservation': False,
            },
            status=200)

        mock_response = {
            "testPaths": [
                [{"type": "target", "name": "XCTestSampleTests"}, {"type": "class", "name": "XCTestSampleTests"}],
                [{"type": "target", "name": "XCTestSampleTests"}, {"type": "class", "name": "XCTestSampleTests2"}],
            ],
            "testRunner": "cts",
            "rest": [
                [{"type": "target", "name": "XCTestSampleUITests"}, {"type": "class", "name": "XCTestSampleUITestsLaunchTests"}],
                [{"type": "target", "name": "XCTestSampleUITests"}, {"type": "class", "name": "XCTestSampleUITests"}],
            ],
            "subsettingId": 123,
            "summary": {
                "subset": {"duration": 30, "candidates": 2, "rate": 30},
                "rest": {"duration": 70, "candidates": 2, "rate": 70}
            },
            "isObservation": False,
        }

        responses.replace(responses.POST,
                          f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/{self.workspace}/subset",
                          json=mock_response,
                          status=200)

        result = self.cli('subset', 'xctest', '--session', self.session_name, '--build', self.build_name,
                          '--get-tests-from-previous-sessions',
                          '--output-exclusion-rules',
                          mix_stderr=False)

        self.assert_success(result)
        self.assert_subset_payload('subset_result.json')
        self.assertEqual(result.stdout, "-skip-testing:XCTestSampleUITests/XCTestSampleUITestsLaunchTests\n-skip-testing:XCTestSampleUITests/XCTestSampleUITests\n")  # noqa: E501
