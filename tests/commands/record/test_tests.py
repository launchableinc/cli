from pathlib import Path
import responses  # type: ignore
import gzip
import sys
import os
from tests.cli_test_case import CliTestCase
from launchable.commands.record.tests import parse_launchable_timeformat, INVALID_TIMESTAMP
from unittest import mock

class TestsTest(CliTestCase):

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_filename_in_error_message(self):
        normal_xml = str(Path(__file__).parent.joinpath(
            '../../data/broken_xml/normal.xml').resolve())
        broken_xml = str(Path(__file__).parent.joinpath(
            '../../data/broken_xml/broken.xml').resolve())
        result = self.cli('record', 'tests', '--build',
                          self.build_name, 'file', normal_xml, broken_xml)

        def remove_backslash(input: str) -> str:
            # Hack for Windowns. They containts double escaped backslash such as \\\\
            if sys.platform == "win32":
                return input.replace("\\", "")
            else:
                return input

        # making sure the offending file path name is being printed.
        self.assertIn(remove_backslash(broken_xml),
                      remove_backslash(result.output))

        # normal.xml
        self.assertIn('open_class_user_test.rb', gzip.decompress(responses.calls[2].request.body).decode())

    def test_parse_launchable_timeformat(self):
        t1 = "2021-04-01T09:35:47.934+00:00"  # 1617269747.934
        t2 = "2021-05-24T18:29:04.285+00:00"  # 1621880944.285
        t3 = "2021-05-32T26:29:04.285+00:00"  # invalid time format

        parse_launchable_time1 = parse_launchable_timeformat(t1)
        parse_launchable_time2 = parse_launchable_timeformat(t2)

        self.assertEqual(parse_launchable_time1.timestamp(), 1617269747.934)
        self.assertEqual(parse_launchable_time2.timestamp(), 1621880944.285)

        self.assertEqual(INVALID_TIMESTAMP, parse_launchable_timeformat(t3))
