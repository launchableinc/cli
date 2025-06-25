import io
from contextlib import contextmanager, redirect_stderr

from launchable.utils.commands import Command
from launchable.utils.fail_fast_mode import FailFastModeValidator
from tests.cli_test_case import CliTestCase


class FailFastModeTest(CliTestCase):
    def test_validate_subset(self):
        validator = FailFastModeValidator(
            command=Command.SUBSET,
            session='session1',
            test_suite='test_suite1',
            is_observation=True,
        )
        stderr = io.StringIO()

        with self.assertRaises(SystemExit) as cm:
            with tmp_set_fail_fast_mode(False), redirect_stderr(stderr):
                # `--observation` option won't be applied but the cli won't be error
                validator.validate()
                self.assertEqual(stderr.getvalue(), "")

            with tmp_set_fail_fast_mode(True), redirect_stderr(stderr):
                validator.validate()
                self.assertEqual(cm.exception.code, 1)
                self.assertIn("ignored", stderr.getvalue())


@contextmanager
def tmp_set_fail_fast_mode(enabled: bool):
    from launchable.utils.fail_fast_mode import _fail_fast_mode_cache, set_fail_fast_mode
    original = _fail_fast_mode_cache
    try:
        set_fail_fast_mode(enabled)
        yield
    finally:
        if original is not None:
            set_fail_fast_mode(original)
