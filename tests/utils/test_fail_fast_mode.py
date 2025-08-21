from contextlib import contextmanager


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
