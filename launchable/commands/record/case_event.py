import datetime
import os
from typing import Callable, Dict
from junitparser import JUnitXml, Failure, Error, Skipped, TestCase, TestSuite
from ...testpath import TestPath


class CaseEvent:
    EVENT_TYPE = "case"
    TEST_SKIPPED = 2
    TEST_PASSED = 1
    TEST_FAILED = 0

    # function that computes TestPath from a test case
    # The 3rd argument is the report file path
    TestPathBuilder = Callable[[TestCase, TestSuite, str], TestPath]

    @staticmethod
    def default_path_builder(base_path) -> TestPathBuilder:
        """
        Obtains a default TestPathBuilder that uses a base directory to relativize the file name
        """

        def f(case: TestCase, suite: TestSuite, report_file: str) -> TestPath:
            classname = case.classname or suite._elem.attrib.get("classname")
            filepath = case._elem.attrib.get(
                "file") or suite._elem.attrib.get("filepath")
            if filepath:
                filepath = os.path.relpath(filepath, start=base_path)

            test_path = []
            if classname:
                test_path.append({"type": "class", "name": classname})
            if filepath:
                test_path.append({"type": "file", "name": filepath})
            if case.name:
                test_path.append(
                    {"type": "testcase", "name": case.name, "_lineno": case._elem.attrib.get("lineno")})
            return test_path

        return f

    @classmethod
    def from_case_and_suite(cls, path_builder: TestPathBuilder, case: TestCase, suite: TestSuite, report_file: str, data: Dict = None) -> Dict:
        "Builds a JSON representation of CaseEvent"

        status = CaseEvent.TEST_FAILED if case.result and any(isinstance(case.result, s) for s in (
            Failure, Error)) else CaseEvent.TEST_SKIPPED if isinstance(case.result, Skipped) else CaseEvent.TEST_PASSED

        return {
            "type": cls.EVENT_TYPE,
            "testPath": path_builder(case, suite, report_file),
            "duration": case.time,
            "status": status,
            "stdout": case.system_out or "",
            "stderr": case.system_err or "",
            "created_at": suite.timestamp or datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "data": data
        }
