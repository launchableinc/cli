import sys
import re
import click
from xml.etree import ElementTree as ET
import json
from pathlib import Path
import glob
import os

from . import launchable
from ..testpath import TestPath


@click.argument('file', type=click.Path(exists=True))
@click.option('--output-regex-files', is_flag=True, help='Output test regex to files')
@click.option('--output-regex-files-dir', type=str, default='.', help='Output directory for test regex')
@click.option('--output-regex-files-size', type=int, default=60 * 1024, help='Max size of each regex file')
@launchable.subset
def subset(client, file, output_regex_files, output_regex_files_dir, output_regex_files_size):
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
            _write_regex_files(output_regex_files_dir, 'subset',
                               output_regex_files_size, output)
            _write_regex_files(output_regex_files_dir, 'rest',
                               output_regex_files_size, rests)
        client.output_handler = handler
        client.run()
    else:
        client.formatter = lambda x: "^{}$".format(x[0]['name'])
        client.seperator = '|'
        client.run()


def _write_regex_files(output_dir, prefix, max_size, paths):
    # Python's regexp spec and CTest's regexp spec would be different, but
    # this escape would work in most of the cases.
    escaped = _group_by_size(
        ['^' + re.escape(tp[0]['name']) + '$' for tp in paths], max_size)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for i, elems in enumerate(escaped):
        with open(os.path.join(output_dir, "{}_{}".format(prefix, i)), 'w') as f:
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
                duration = duration_node.text if duration_node is not None else '0'

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
