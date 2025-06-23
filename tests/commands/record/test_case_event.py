
import unittest
from io import StringIO
from unittest import mock

from launchable.commands.record.case_event import CaseEvent

UNKNOWN_TIMEZONE_WARNING = "UnknownTimezoneWarning"


class TestCaseEventTimestamp(unittest.TestCase):
    def test_timestamp_with_known_abbreviation(self):
        # Use a known abbreviation from COMMON_TIMEZONES
        ts = "2024-06-23T12:34:56.789 PDT"  # PDT is in COMMON_TIMEZONES
        with mock.patch('sys.stderr', new=StringIO()) as stderr:
            result = CaseEvent.create(
                test_path=[], duration_secs=1.0, status=CaseEvent.TEST_PASSED, timestamp=ts
            )
            # Should parse to ISO format with correct offset
            self.assertTrue(result["createdAt"].startswith("2024-06-23T12:34:56.789"))
            self.assertIn("-07:00", result["createdAt"])
            # Should NOT output a warning to stderr
            self.assertNotIn(UNKNOWN_TIMEZONE_WARNING, stderr.getvalue())

    def test_timestamp_with_unknown_abbreviation(self):
        # Use an unknown abbreviation
        ts = "2024-06-23T12:34:56.789 XYZ"  # XYZ is not in COMMON_TIMEZONES
        with mock.patch('sys.stderr', new=StringIO()) as stderr:
            result = CaseEvent.create(
                test_path=[], duration_secs=1.0, status=CaseEvent.TEST_PASSED, timestamp=ts
            )
            # Should output a warning to stderr
            self.assertIn(UNKNOWN_TIMEZONE_WARNING, stderr.getvalue())
            # The createdAt may still start with the input timestamp, but should not have a timezone offset
            self.assertTrue(result["createdAt"].startswith("2024-06-23T12:34:56.789"))
