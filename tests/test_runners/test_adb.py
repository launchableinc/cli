import os
from unittest import mock

import responses  # type: ignore

from smart_tests.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class AdbTest(CliTestCase):
    subset_input = """INSTRUMENTATION_STATUS: class=com.example.sampleapp.ExampleInstrumentedTest2
INSTRUMENTATION_STATUS: current=1
INSTRUMENTATION_STATUS: id=AndroidJUnitRunner
INSTRUMENTATION_STATUS: numtests=2
INSTRUMENTATION_STATUS: stream=
com.example.sampleapp.ExampleInstrumentedTest2:
INSTRUMENTATION_STATUS: test=useAppContext
INSTRUMENTATION_STATUS_CODE: 1
INSTRUMENTATION_STATUS: class=com.example.sampleapp.ExampleInstrumentedTest2
INSTRUMENTATION_STATUS: current=1
INSTRUMENTATION_STATUS: id=AndroidJUnitRunner
INSTRUMENTATION_STATUS: numtests=2
INSTRUMENTATION_STATUS: stream=.
INSTRUMENTATION_STATUS: test=useAppContext
INSTRUMENTATION_STATUS_CODE: 0
INSTRUMENTATION_STATUS: class=com.example.sampleapp.ExampleInstrumentedTest
INSTRUMENTATION_STATUS: current=2
INSTRUMENTATION_STATUS: id=AndroidJUnitRunner
INSTRUMENTATION_STATUS: numtests=2
INSTRUMENTATION_STATUS: stream=
com.example.sampleapp.ExampleInstrumentedTest:
INSTRUMENTATION_STATUS: test=useAppContext
INSTRUMENTATION_STATUS_CODE: 1
INSTRUMENTATION_STATUS: class=com.example.sampleapp.ExampleInstrumentedTest
INSTRUMENTATION_STATUS: current=2
INSTRUMENTATION_STATUS: id=AndroidJUnitRunner
INSTRUMENTATION_STATUS: numtests=2
INSTRUMENTATION_STATUS: stream=.
INSTRUMENTATION_STATUS: test=useAppContext
INSTRUMENTATION_STATUS_CODE: 0
INSTRUMENTATION_RESULT: stream=

Time: 0.011

OK (2 tests)


INSTRUMENTATION_CODE: -1
"""

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
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

        result = self.cli(
            'subset',
            'adb',
            '--build',
            self.build_name,
            '--session',
            self.session_name,
            '--target',
            '10%',
            input=self.subset_input)
        self.assert_success(result)
        self.assert_subset_payload('subset_result.json')
