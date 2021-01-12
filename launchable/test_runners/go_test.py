from junitparser import TestCase, TestSuite
import sys
from . import launchable


@launchable.subset
def subset(client):
    for case in sys.stdin:
        # Aboid last line such s `ok      github.com/launchableinc/rocket-car-gotest      0.268s`
        if not ' ' in case:
            client.test_path({'type': 'testcase', 'name': case.rstrip('\n')})
    client.run()
