import datetime
from junitparser import JUnitXml, Failure, Error, Skipped, TestCase
import os


class CaseEvent:
    EVENT_TYPE = "case"
    TEST_SKIPPED = 2
    TEST_PASSED = 1
    TEST_FAILED = 0

    @classmethod
    def from_case_and_suite(cls, case, suite, base_path):
        status = CaseEvent.TEST_FAILED if case.result and any(isinstance(case.result, s) for s in (
            Failure, Error)) else CaseEvent.TEST_SKIPPED if isinstance(case.result, Skipped) else CaseEvent.TEST_PASSED
        filepath = case._elem.attrib.get(
            "file") or suite._elem.attrib.get("filepath")
        if filepath:
            filepath = os.path.relpath(filepath, start=base_path),
        return CaseEvent(
            case.name,
            case.time,
            status,
            case.system_out or "",
            case.system_err or "",
            suite.timestamp,
            case.classname or suite._elem.attrib.get("classname"),
            filepath,
            case._elem.attrib.get("lineno")
        )

    def __init__(self, test_name, duration, status, stdout, stderr, timestamp, classname=None, filename=None, lineno=None):
        self.testName = test_name
        self.duration = duration
        self.status = status
        self.stdout = stdout
        self.stderr = stderr
        self.created_at = timestamp or datetime.datetime.now(
            datetime.timezone.utc).isoformat()

        self.data = {}
        test_path = []
        if classname:
            test_path.append({"type": "class", "name": classname})
        if filename:
            test_path.append({"type": "file", "name": filename})
        if test_name:
            test_path.append(
                {"type": "testcase", "name": test_name, "lineno": lineno})

        self.data["test_paths"] = test_path

    def to_json(self):
        return {
            "type": self.EVENT_TYPE,
            "testName": self.testName,
            "duration": self.duration,
            "status": self.status,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "created_at": self.created_at,
            "data": self.data
        }
