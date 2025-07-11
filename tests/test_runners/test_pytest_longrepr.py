import json
import tempfile
import unittest

from launchable.test_runners.pytest import PytestJSONReportParser


class DummyClient:
    pass


class TestPytestJSONReportParserLongrepr(unittest.TestCase):
    def setUp(self):
        self.parser = PytestJSONReportParser(DummyClient())

    def parse_line(self, data):
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
            f.write(json.dumps(data) + "\n")
            f.flush()
            results = list(self.parser.parse_func(f.name))
        return results

    def test_longrepr_dict_message_and_text(self):
        data = self.make_event_data(
            {
                "reprcrash": {"message": "AssertionError: fail"},
                "reprtraceback": {
                    "reprentries": [{"data": {"lines": ["line1", "line2"]}}]
                },
            }
        )
        events = self.parse_line(data)
        self.assert_stderr(events, "AssertionError: fail\nline1\nline2")

    def test_longrepr_dict_only_message(self):
        data = self.make_event_data({"reprcrash": {"message": "Only message"}})
        events = self.parse_line(data)
        self.assert_stderr(events, "Only message")

    def test_longrepr_dict_only_text(self):
        data = self.make_event_data(
            {"reprtraceback": {"reprentries": [{"data": {"lines": ["text only"]}}]}}
        )
        events = self.parse_line(data)
        self.assert_stderr(events, "text only")

    def test_longrepr_list(self):
        data = self.make_event_data(["file.py", 10, "list message"])
        events = self.parse_line(data)
        self.assert_stderr(events, "list message")

    def test_longrepr_str(self):
        data = self.make_event_data("string message")
        events = self.parse_line(data)
        self.assert_stderr(events, "string message")

    def assert_stderr(self, events, expected_stderr):
        self.assertEqual(events[0]["stderr"], expected_stderr)

    def make_event_data(self, longrepr):
        return {
            "nodeid": "tests/test_sample.py::test_fail",
            "when": "call",
            "outcome": "failed",
            "longrepr": longrepr,
        }
