import click
import os
import sys
from . import launchable
from junitparser import TestSuite, JUnitXml


@click.argument('reports', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, reports):
    for r in reports:
        client.report(r)

    def testsuites(xml) -> [TestSuite]:
        testsuites = []
        if isinstance(xml, JUnitXml):
            filepath = xml._elem.find(
                './/testsuite[@name="Root Suite"]').get("file")
            for suite in xml:
                suite._elem.attrib.update(
                    {"filepath": filepath})
                testsuites.append(suite)
        else:
            # TODO: what is a Pythonesque way to do this?
            assert False
        return testsuites

    client.testsuites = testsuites
    client.run()


@launchable.subset
def subset(client):
    # read lines as test file names
    for t in sys.stdin:
        client.test_path(t.rstrip("\n"))

    client.separator = ','
    client.run()
