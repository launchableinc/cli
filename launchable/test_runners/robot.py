import click
from . import launchable
from xml.etree import ElementTree as ET
import os
from datetime import datetime
from junitparser import JUnitXml  # type: ignore
from ..testpath import TestPath


def parse_func(p: str) -> ET.ElementTree:
    datetime_format = '%Y%m%d %H:%M:%S.%f'

    original_tree = ET.parse(p)
    testsuite = ET.Element("testsuite", {"name": "robot"})
    for suite in original_tree.findall("suite/suite"):
        suite_name = suite.get('name')
        for test in suite.iter("test"):
            test_name = test.get('name')

            status_node = test.find('status')
            status = status_node.get(
                'status') if status_node is not None else None

            nested_status_node = test.find('./kw/status')
            nested_status = nested_status_node.get(
                'status') if nested_status_node is not None else None

            if status != None:
                start_time_str = status_node.get(
                    'starttime') if status_node is not None else ''
                end_time_str = status_node.get(
                    'endtime') if status_node is not None else ''

                if start_time_str != '' and end_time_str != '':
                    start_time = datetime.strptime(
                        str(start_time_str), datetime_format)
                    end_time = datetime.strptime(
                        str(end_time_str), datetime_format)

                    duration = end_time - start_time

                testcase = ET.SubElement(testsuite, "testcase", {
                    "name": str(test_name),
                    "classname": str(suite_name),
                    "time": str(duration.microseconds / 1000 / 1000) if duration is not None else '0',
                })

                if status == "FAIL":
                    failure = ET.SubElement(testcase, 'failure')

                    msg = test.find('kw/msg')
                    failure.text = msg.text if msg is not None else ''
                if status == "NOT_RUN" or nested_status == 'NOT_RUN':
                    skipped = ET.SubElement(testcase, "skipped")

    return ET.ElementTree(testsuite)


@click.argument('reports', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, reports):
    for r in reports:
        client.report(r)

    client.junitxml_parse_func = parse_func
    client.run()


@click.argument('reports', required=True, nargs=-1)
@launchable.subset
def subset(client, reports):
    for r in reports:
        suite = JUnitXml.fromfile(r, parse_func)

        for case in suite:
            cls_name = case._elem.attrib.get("classname")
            name = case._elem.attrib.get('name')
            if cls_name != '' and name != '':
                client.test_path([{'type': 'class', 'name': cls_name}, {
                                 'type': 'testcase', 'name': name}])

    client.formatter = robot_formatter
    client.separator = " "
    client.run()


@launchable.split_subset
def split_subset(client):
    client.formatter = robot_formatter
    client.separator = " "
    client.run()


def robot_formatter(x: TestPath):
    cls_name = ''
    case = ''
    for path in x:
        t = path['type']
        if t == 'class':
            cls_name = path['name']
        if t == 'testcase':
            case = path['name']

    if cls_name != '' and case != '':
        return "-s '{}' -t '{}'".format(
            cls_name, case)

    return ''
