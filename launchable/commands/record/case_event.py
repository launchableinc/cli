import datetime
import os
import sys
from typing import Callable, Dict
from junitparser import Failure, Error, Skipped, TestCase, TestSuite  # type: ignore
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
            classname = case._elem.attrib.get("classname") or suite._elem.attrib.get("classname")
            filepath = case._elem.attrib.get(
                "file") or suite._elem.attrib.get("filepath")
            if filepath:
                filepath = os.path.relpath(filepath, start=base_path)

            test_path = []
            if filepath:
                test_path.append({"type": "file", "name": filepath})
            if classname:
                test_path.append({"type": "class", "name": classname})
            if case.name:
                test_path.append(
                    {"type": "testcase", "name": case._elem.attrib.get("name")})
            return test_path

        return f

    @classmethod
    def from_case_and_suite(cls, path_builder: TestPathBuilder, case: TestCase, suite: TestSuite, report_file: str, data: Dict = None) -> Dict:
        "Builds a JSON representation of CaseEvent from JUnitPaser objects"

        # TODO: reconsider the initial value of the status.
        status = CaseEvent.TEST_PASSED
        for r in case.result:
            if any(isinstance(r, s) for s in (Failure, Error)):
                status = CaseEvent.TEST_FAILED
                break
            elif isinstance(r, Skipped):
                status = CaseEvent.TEST_SKIPPED

        def path_canonicalizer(test_path: TestPath) -> TestPath:
            if sys.platform == "win32":
                for p in test_path:
                    p['name'] = p['name'].replace("\\", "/")

            return test_path

        return CaseEvent.create(
            path_canonicalizer(path_builder(case, suite, report_file)), case.time, status,
            case._elem.attrib.get("system-out"),
            case._elem.attrib.get("system-err"),
            suite.timestamp, data)

    @classmethod
    def create(cls, test_path: TestPath, duration_secs: float, status,
               stdout:str = None, stderr:str = None, timestamp: str = None, data: Dict = None) -> Dict:
        """
        Builds a JSON representation of CaseEvent from arbitrary set of values

        status:    TEST_FAILED or TEST_PASSED
        timestamp: ISO-8601 formatted date
        data:      arbitrary data to be submitted to the server. reserved for future enhancement.
        """
        return {
            "type": cls.EVENT_TYPE,
            "testPath": test_path,
            "duration": duration_secs,
            "status": status,
            "stdout": stdout or "",
            "stderr": stderr or "",
            "created_at": timestamp or datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "data": data
        }
