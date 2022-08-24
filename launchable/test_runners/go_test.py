from . import launchable
import re
from ..utils.logger import Logger


@launchable.subset
def subset(client):
    logger = Logger()

    # NOTE: This should be using package name + test function name to specify
    # which tests to run. However, the initial integration is created so that we
    # only specify the test function names. This can result in matching some
    # extra tests in multiple packages. However, in order to keep the initial
    # way of the integration, we cannot change this. Try to do the best.
    test_cases = []
    for line in client.stdin():
        if not ' ' in line:
            test_cases.append(line.strip('\n'))
        else:
            parts = re.split('\s+', line)
            if len(parts) >= 2:
                package = parts[1].split('/')[-1]
                for test_case in test_cases:
                    client.test_path([{'type': 'class', 'name': package}, {
                                     'type': 'testcase', 'name': test_case}])
            else:
                logger.warning(
                    "Cannot extract the package from the input. This may result in missing some tests.")
            test_cases = []
    client.formatter = lambda x: "^{}$".format(x[1]['name'])
    client.separator = '|'
    client.run()


split_subset = launchable.CommonSplitSubsetImpls(
    __name__, formatter=lambda x: "^{}$".format(x[1]['name']), seperator='|').split_subset()
record_tests = launchable.CommonRecordTestImpls(__name__).report_files()
