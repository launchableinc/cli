import subprocess


def check_output(*args, **kwargs):
    """A wrapper for subprocess.check_output

    In Windows, subprocess.check_output is used internally in one of those
    dependencies. If we mock out subprocess.check_output, it also traps those
    internall calls, making tests fail. This wrapper is a point to mock only
    launchable CLI initiated calls.
    """
    return subprocess.check_output(*args, **kwargs)
