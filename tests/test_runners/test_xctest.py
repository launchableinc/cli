import os
from unittest import mock

import responses  # type: ignore

from launchable.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class XCTestTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ,
                     {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_record_test(self):
        result = self.cli('record', 'tests', '--session', self.session,
                          'xctest', str(self.test_files_dir.joinpath("junit.xml")))

        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')

    @responses.activate
    @mock.patch.dict(os.environ,
                     {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_subset(self):
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

        responses.replace(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(
            get_base_url(),
            self.organization,
            self.workspace),
            json=mock_response,
            status=200)

        result = self.cli('subset',
                          '--session', self.session,
                          '--get-tests-from-previous-sessions',
                          '--output-exclusion-rules',
                          'xctest',
                          mix_stderr=False)

        self.assert_success(result)
        self.assert_subset_payload('subset_result.json')
        self.assertEqual(result.stdout, "-skip-testing:XCTestSampleUITests/XCTestSampleUITestsLaunchTests\n-skip-testing:XCTestSampleUITests/XCTestSampleUITests\n")  # noqa: E501
