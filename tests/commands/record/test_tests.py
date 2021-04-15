from pathlib import Path
import responses # type: ignore
import gzip
import sys
from tests.cli_test_case import CliTestCase


class TestsTest(CliTestCase):

    @responses.activate
    def test_filename_in_error_message(self):        
        normal_xml = str(Path(__file__).parent.joinpath('../../data/broken_xml/normal.xml').resolve())
        broken_xml = str(Path(__file__).parent.joinpath('../../data/broken_xml/broken.xml').resolve())
        result = self.cli('record', 'tests', '--build', self.build_name, 'file', normal_xml, broken_xml)

        def remove_backslash(input: str) -> str:
            # Hack for Windowns. They containts double escaped backslash such as \\\\
            if sys.platform == "win32":
                return input.replace("\\", "")
            else:
                return input

        # making sure the offending file path name is being printed.
        self.assertIn(remove_backslash(broken_xml), remove_backslash(result.output))

        # normal.xml
        self.assertIn('open_class_user_test.rb', gzip.decompress(b''.join(responses.calls[1].request.body)).decode())
