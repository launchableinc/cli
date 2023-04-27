import datetime
import sys
from typing import Callable, Dict, Optional

from junitparser import Error, Failure, Skipped, TestCase, TestSuite  # type: ignore

from ...testpath import FilePathNormalizer, TestPath

POSSIBLE_RESULTS = (Failure, Error, Skipped)

CaseEventType = Dict[str, str]


class CaseEvent:
    EVENT_TYPE = "case"
    TEST_SKIPPED = 2
    TEST_PASSED = 1
    TEST_FAILED = 0

    STATUS_MAP = {
        'TEST_SKIPPED': TEST_SKIPPED,
        'TEST_PASSED': TEST_PASSED,
        'TEST_FAILED': TEST_FAILED,
    }

    # function that computes TestPath from a test case
    # The 3rd argument is the report file path
    TestPathBuilder = Callable[[TestCase, TestSuite, str], TestPath]

    @staticmethod
    def default_path_builder(
            file_path_normalizer: FilePathNormalizer) -> TestPathBuilder:
        """
        Obtains a default TestPathBuilder that uses a base directory to relativize the file name
        """

        def f(case: TestCase, suite: TestSuite, report_file: str) -> TestPath:
            classname = case._elem.attrib.get("classname") or suite._elem.attrib.get("classname")
            filepath = case._elem.attrib.get("file") or suite._elem.attrib.get("filepath")
            if filepath:
                filepath = file_path_normalizer.relativize(filepath)

            test_path = []
            if filepath:
                test_path.append({"type": "file", "name": filepath})
            if classname:
                test_path.append({"type": "class", "name": classname})
            if case.name:
                test_path.append({"type": "testcase", "name": case._elem.attrib.get("name")})
            return test_path

        return f

    @classmethod
    def from_case_and_suite(
        cls,
        path_builder: TestPathBuilder,
        case: TestCase,
        suite: TestSuite,
        report_file: str,
        data: Optional[Dict] = None,
    ) -> Dict:
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

        def stdout(case: TestCase) -> str:
            """
            case for:
                <testcase>
                <system-out>...</system-out>
                </testcase>
            """
            if case.system_out is not None:
                return case.system_out

            return ""

        def stderr(case: TestCase) -> str:
            """
            case for:
                <testcase>
                <system-err>...</system-err>
                </testcase>
            """
            if case.system_err is not None:
                return case.system_err

            """
            case for:
                <testcase>
                <failure message="...">...</failure>
                </testcase>
            """
            stderr = ""
            for result in case.result:
                if type(result) in POSSIBLE_RESULTS:
                    if result.message and result.text:
                        stderr = stderr + result.message + "\n" + result.text
                    elif result.message:
                        stderr = stderr + result.message + "\n"
                    elif result.text:
                        stderr = stderr + result.text

            return stderr

        return CaseEvent.create(
            path_canonicalizer(path_builder(case, suite, report_file)), case.time, status,
            stdout(case),
            stderr(case),
            suite.timestamp, data)

    @classmethod
    def create(cls, test_path: TestPath, duration_secs: float, status,
               stdout: Optional[str] = None, stderr: Optional[str] = None,
               timestamp: Optional[str] = None, data: Optional[Dict] = None) -> Dict:
        """
        Builds a JSON representation of CaseEvent from arbitrary set of values

        status:    TEST_FAILED or TEST_PASSED
        timestamp: ISO-8601 formatted date
        data:      arbitrary data to be submitted to the server. reserved for future enhancement.
        """
        return {
            "type": cls.EVENT_TYPE,
            "testPath": test_path,
            "duration": duration_secs if duration_secs and duration_secs >= 0.0 else 0.0,
            "status": status,
            "stdout": stdout or "",
            "stderr": stderr or "",
            "created_at": timestamp or datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "data": data
        }
