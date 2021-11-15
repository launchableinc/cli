import os
from typing import List
from xml.etree import ElementTree as ET
import click

from launchable.utils.sax import Element
from . import launchable
from pathlib import Path
import itertools
from copy import deepcopy

REPORT_FILE_PREFIX = "TEST-"

subset = launchable.CommonSubsetImpls(__name__).scan_files('*_feature')
split_subset = launchable.CommonSplitSubsetImpls(__name__).split_subset()


@click.argument('reports', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, reports):
    report_file_and_test_file_map = {}
    for report in reports:
        if REPORT_FILE_PREFIX not in report:
            click.echo(
                "{} was load skipped because it doesn't look like a report file.".format(report), err=True)
            continue

        report_file = os.path.basename(report)
        report_file = report_file.lstrip(REPORT_FILE_PREFIX)
        report_file = os.path.splitext(report_file)[0]
        test_file = _find_test_file_from_report_file(report_file)
        if test_file:
            report_file_and_test_file_map[report] = test_file
            client.report(report)

    def parse_func(report: str) -> ET.ElementTree:
        tree = ET.parse(report)
        for case in tree.findall("testcase"):
            case.attrib["file"] = str(report_file_and_test_file_map[report])

        return tree

    client.junitxml_parse_func = parse_func
    client.run()


def _find_test_file_from_report_file(report_file: str) -> Path:
    list = _create_file_candidate_list(report_file)
    for l in list:
        f = Path(l + ".feature")
        if f.exists():
            return f

    return None


def _create_file_candidate_list(file: str) -> List[str]:
    list = [""]
    hyphen_count = file.count("-")
    hc = 0
    count = 0
    for c in file:
        if c == "-":
            l = len(list)
            list += deepcopy(list)
            for i in range(l):
                list[i] += '-'
            for i in range(l, len(list)):
                list[i] += '/'
            hc = hc + 1
        elif hyphen_count <= hc:
            list[i] += file[count:len(file)]
            break
        else:
            for i in range(len(list)):
                list[i] += c
        count = count + 1
    return list
