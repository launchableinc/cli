import os
from unittest import mock

import responses  # type: ignore

from smart_tests.utils.session import read_session, write_build
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
        # emulate launchable record build
        write_build(self.build_name)

        result = self.cli('subset', 'adb', '--target', '10%', input=self.subset_input)
        self.assert_success(result)

        self.assertEqual(read_session(self.build_name), self.session)
        self.assert_subset_payload('subset_result.json')
