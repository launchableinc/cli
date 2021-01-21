import click
import os
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
            for suite in xml:
                if suite.name == "Root Suite":
                    filepath = suite._elem.attrib.get("file")
                    continue
                if filepath:
                    suite._elem.attrib.update(
                        {"filepath": filepath})
                    testsuites.append(suite)
        else:
            # TODO: what is a Pythonesque way to do this?
            assert False
        return testsuites

    client.testsuites = testsuites
    client.run()
