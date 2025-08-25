import glob
import json
import os
import re
from pathlib import Path
from typing import Annotated, List
from xml.etree import ElementTree as ET

import typer

from . import smart_tests


@smart_tests.subset
def subset(
    client,
    file: Annotated[str, typer.Argument(
        help="JSON file to process"
    )],
    output_regex_files: Annotated[bool, typer.Option(
        "--output-regex-files",
        help="Output test regex to files"
    )] = False,
    output_regex_files_dir: Annotated[str, typer.Option(
        "--output-regex-files-dir",
        help="Output directory for test regex"
    )] = ".",
    output_regex_files_size: Annotated[int, typer.Option(
        "--output-regex-files-size",
        help="Max size of each regex file"
    )] = 60 * 1024,
):
    if file:
        with Path(file).open() as json_file:
            data = json.load(json_file)
    else:
        data = json.loads(client.stdin())

    for test in data['tests']:
        case = test['name']
        client.test_path([{'type': 'testcase', 'name': case}])

    if output_regex_files:
        def handler(output, rests):
            _write_regex_files(output_regex_files_dir, 'subset', output_regex_files_size, output)
            _write_regex_files(output_regex_files_dir, 'rest', output_regex_files_size, rests)
        client.output_handler = handler
        client.run()
    else:
        client.formatter = lambda x: f"^{x[0]['name']}$"
        client.seperator = '|'
        client.run()


def _write_regex_files(output_dir, prefix, max_size, paths):
    # Python's regexp spec and CTest's regexp spec would be different, but
    # this escape would work in most of the cases.
    escaped = _group_by_size(['^' + re.escape(tp[0]['name']) + '$' for tp in paths], max_size)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for i, elems in enumerate(escaped):
        with open(os.path.join(output_dir, f"{prefix}_{i}"), 'w') as f:
            f.write('|'.join(elems) + '\n')


def _group_by_size(elems, max_size):
    ret = []
    curr = []
    curr_size = 0
    for elem in elems:
        # +1 for the separator
        if max_size < curr_size + len(elem) + 1:
            ret.append(curr)
            curr = [elem]
            curr_size = len(elem)
        else:
            curr.append(elem)
            curr_size = len(elem) + 1
    if len(curr) != 0:
        ret.append(curr)
    return ret


@smart_tests.record.tests
def record_tests(
    client,
    source_roots: Annotated[List[str], typer.Argument(
        help="Source root directories or files to process"
    )],
):
    for root in source_roots:
        match = False
        for t in glob.iglob(root, recursive=True):
            match = True
            if os.path.isdir(t):
                client.scan(t, "*.xml")
            else:
                client.report(t)
        if not match:
            typer.echo(f"No matches found: {root}", err=True)

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
                duration_node = test.find("./Results/NamedMeasurement[@name=\"Execution Time\"]/Value")
                measurement_node = test.find("Results/Measurement/Value")

                stdout = measurement_node.text if measurement_node is not None else ''
                duration = duration_node.text if duration_node is not None else '0'

                testcase = ET.SubElement(testsuite, "testcase",
                                         {"name": test_name.text or '',
                                          "time": str(duration),
                                          "system-out": stdout or '',
                                          })

                system_out = ET.SubElement(testcase, "system-out")
                system_out.text = stdout

                test_count += 1
                status = test.get("Status")
                if status is not None:
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
