import sys
import click
from xml.etree import ElementTree as ET
import json
from pathlib import Path
import glob
import os

from . import launchable
from ..testpath import TestPath

@click.argument('file', type=click.Path(exists=True))
@launchable.subset
def subset(client, file):
    if file:
        with Path(file).open() as json_file:
            data = json.load(json_file)
    else:
        data = json.loads(sys.stdin)

    for test in data['tests']:
        case = test['name']
        client.test_path([{'type': 'testcase', 'name': case}])

    client.formatter = lambda x: "^{}$".format(x[0]['name'])
    client.seperator = '|'
    client.run()


@click.argument('source_roots', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, source_roots):
    for root in source_roots:
        match = False
        for t in glob.iglob(root, recursive=True):
            match = True
            if os.path.isdir(t):
                client.scan(t, "*.xml")
            else:
                client.report(t)
        if not match:
            click.echo("No matches found: {}".format(root), err=True)

    def parse_func(p: str) -> ET.Element:
        """
        Convert from CTest own XML format to JUnit XML format
        The projections of these properties are based on
            https://github.com/rpavlik/jenkins-ctest-plugin/blob/master/ctest-to-junit.xsl
        """
        original_tree = ET.parse(p)

        testsuite = ET.Element("testsuite", {"name": "CTest"})
        test_count = 0
        failure_count = 0

        for test in original_tree.findall("./Testing/Test"):
            test_name = test.find("Name")
            duration = test.find(
                "./Results/NamedMeasurement[@name=\"Execution Time\"]/Value")
            measurement = test.find("Results/Measurement/Value")
            testcase = ET.SubElement(testsuite, "testcase", {
                                     "name": test_name.text, "time": duration.text, "system-out": measurement.text})

            system_out = ET.SubElement(testcase, "system-out")
            system_out.text = measurement.text

            test_count += 1

            if test.get("Status") != "passed":
                failure = ET.SubElement(testcase, "failure")
                failure.text = measurement.text

                failure_count += 1

        testsuite.attrib.update({
                                "tests": test_count,
                                "time": 0,
                                "failures": failure_count,
                                "errors": 0,
                                "skipped": 0
                                })

        return ET.ElementTree(testsuite)

    client._junitxml_parse_func = parse_func
    client.run()
