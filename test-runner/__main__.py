import sys
from xmlrunner.runner import XMLTestProgram, XMLTestRunner


class LaunchableTestRunner(XMLTestRunner):
    def __init__(self, **kwargs):
        super().__init__(output='test-results', outsuffix="", **kwargs)


class LaunchableTestProgram(XMLTestProgram):
    def __init__(self, *args, **kwargs):
        kwargs["testRunner"] = LaunchableTestRunner
        super().__init__(*args, **kwargs)


LaunchableTestProgram(module=None)
