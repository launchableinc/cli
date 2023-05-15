from launchable.test_runners import launchable


@launchable.subset
def subset(client):
    print("hi")


@launchable.record.tests
def record_tests(client):
    print("hi")
