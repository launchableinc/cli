from pathlib import Path
import responses, traceback

from tests.cli_test_case import CliTestCase


class TestsTest(CliTestCase):

    @responses.activate
    def test_filename_in_error_message(self):
        broken_xml = str(Path(__file__).parent.joinpath('../../data/broken.xml').resolve())
        self.cli('record', 'tests', '--build', self.build_name, 'file', broken_xml)
        # mock doesn't evaluate generator so we need to do so here
        g = responses.calls[1].request.body
        try:
            b''.join(g)
        except Exception as e:
            # making sure the offending file path name is being printed.
            self.assertIn(broken_xml, traceback.format_exc())
        else:
            self.fail("Expected to see an error")
