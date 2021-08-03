import sys
from xmlrunner.runner import XMLTestProgram, XMLTestRunner

"""
This project use xmlrunner command to publish xml test report.
However, the xmlrunner adds a date time suffix to test suite automatically.
Although, there are the same test cases, the Launchable realizes the differect test cases.
So I add this wrapper command to disable suffix.
"""


class LaunchableTestRunner(XMLTestRunner):
    def __init__(self, **kwargs):
        super().__init__(output='test-results', outsuffix="", **kwargs)


class LaunchableTestProgram(XMLTestProgram):
    def __init__(self, *args, **kwargs):
        kwargs["testRunner"] = LaunchableTestRunner
        super().__init__(*args, **kwargs)


LaunchableTestProgram(module=None)
