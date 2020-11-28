import datetime
from junitparser import JUnitXml, Failure, Error, Skipped, TestCase


class CaseEvent:
    EVENT_TYPE = "case"
    TEST_PASSED = 1
    TEST_FAILED = 0

    @classmethod
    def from_case(cls, case):
        event_type = CaseEvent.TEST_FAILED if case.result and any(isinstance(
            case.result, s) for s in (Failure, Error)) else CaseEvent.TEST_PASSED
        stdout = None
        stderr = case.result.message if case.result else None
        return CaseEvent(
            case.name,
            case.time,
            event_type,
            stdout,
            stderr
        )

    def __init__(self, test_name, duration, status, stdout, stderr):
        self.testName = test_name
        self.duration = duration
        self.status = status
        self.stdout = stdout
        self.stderr = stderr
        self.created_at = datetime.datetime.now(
            datetime.timezone.utc).isoformat()

    def to_body(self):
        return {
            "type": self.EVENT_TYPE,
            "testName": self.testName,
            "duration": self.duration,
            "status": self.status,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "created_at": self.created_at
        }
