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
        data = json.loads(client.stdin())

    for test in data['tests']:
        case = test['name']
        client.test_path([{'type': 'testcase', 'name': case}])

    client.formatter = lambda x: "^{}$".format(x[0]['name'])
    client.seperator = '|'
    client.run()


split_subset = launchable.CommonSplitSubsetImpls(
    __name__, formatter=lambda x: "^{}$".format(x[0]['name']), seperator='|').split_subset()


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

    def parse_func(p: str) -> ET.ElementTree:
        """
        Convert from CTest own XML format to JUnit XML format
        The projections of these properties are based on
            https://github.com/rpavlik/jenkins-ctest-plugin/blob/master/ctest-to-junit.xsl
        """
        original_tree = ET.parse(p)

        testsuite = ET.Element("testsuite", {"name": "CTest"})
        test_count = 0
        failure_count = 0
        skip_count = 0

        for test in original_tree.findall("./Testing/Test"):
            test_name = test.find("Name")
            if test_name is not None:
                duration_node = test.find(
                    "./Results/NamedMeasurement[@name=\"Execution Time\"]/Value")
                measurement_node = test.find("Results/Measurement/Value")

                stdout = measurement_node.text if measurement_node is not None else ''
                duration = duration_node.text if duration_node  is not None else '0'

                testcase = ET.SubElement(testsuite, "testcase", {
                                        "name": test_name.text or '', "time": str(duration), "system-out": stdout or ''})

                system_out = ET.SubElement(testcase, "system-out")
                system_out.text = stdout

                test_count += 1
                status = test.get("Status")
                if status != None:
                    if status == "failed":
                        failure = ET.SubElement(testcase, "failure")
                        failure.text = stdout

                        failure_count += 1

                    if status == "notrun":
                        skipped = ET.SubElement(testcase, "skipped")
                        skipped.text = stdout

                        skip_count += 1

        testsuite.attrib.update({
                                "tests": str(test_count),
                                "time": "0",
                                "failures": str(failure_count),
                                "errors": "0",
                                "skipped": str(skip_count)
                                })

        return ET.ElementTree(testsuite)

    client.junitxml_parse_func = parse_func
    client.run()
