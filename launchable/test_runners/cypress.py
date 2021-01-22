import click
import os
import sys
from . import launchable
from junitparser import TestSuite, JUnitXml
from xml.etree import ElementTree as ET


@click.argument('reports', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, reports):
    for r in reports:
        client.report(r)

    def parse_func(p: str) -> ET.Element:
        tree = ET.parse(p)
        for suites in tree.iter("testsuites"):
            filepath = suites.find(
                './/testsuite[@name="Root Suite"]').get("file")
            for suite in suites:
                suite.attrib.update({"filepath": filepath})
        return tree

    client._junitxml_parse_func = parse_func
    client.run()


@launchable.subset
def subset(client):
    # read lines as test file names
    for t in sys.stdin:
        client.test_path(t.rstrip("\n"))

    client.separator = ','
    client.run()
