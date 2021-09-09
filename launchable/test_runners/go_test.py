from . import launchable


@launchable.subset
def subset(client):
    for case in client.stdin():
        # Avoid last line such as `ok      github.com/launchableinc/rocket-car-gotest      0.268s`
        if not ' ' in case:
            client.test_path([{'type': 'testcase', 'name': case.rstrip('\n')}])

    client.formatter = lambda x: "^{}$".format(x[0]['name'])
    client.separator = '|'
    client.run()


split_subset = launchable.CommonSplitSubsetImpls(
    __name__, formatter=lambda x: "^{}$".format(x[0]['name']), seperator='|').split_subset()
record_tests = launchable.CommonRecordTestImpls(__name__).report_files()
