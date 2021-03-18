import click
from . import launchable
from xml.etree import ElementTree as ET
import os
from datetime import datetime
from junitparser import JUnitXml


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

            dryrun_status_node = test.find('./kw/status')
            dryrun_status = dryrun_status_node.get(
                'status') if dryrun_status_node is not None else None

            if status != None:
                start_time_str = status_node.get('starttime')
                end_time_str = status_node.get('endtime')

                if start_time_str != '' and end_time_str != '':
                    start_time = datetime.strptime(
                        start_time_str, datetime_format)
                    end_time = datetime.strptime(
                        end_time_str, datetime_format)

                    duration = end_time - start_time

                testcase = ET.SubElement(testsuite, "testcase", {
                    "name": test_name,
                    "classname": suite_name,
                    "time": str(duration.microseconds / 1000 / 1000) if duration is not None else '0',
                })

                if status == "FAIL":
                    failure = ET.SubElement(testcase, 'failure')
                    failure.text = test.find(
                        'kw/msg').text if test.find('kw/msg') is not None else ''
                if status == "NOT_RUN" or dryrun_status == 'NOT_RUN':
                    skipped = ET.SubElement(testcase, "skipped")

    return ET.ElementTree(testsuite)


@click.argument('reports', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, reports):
    for r in reports:
        client.report(r)

    client._junitxml_parse_func = parse_func
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

    client.formatter = lambda x: "-s '{}' -t '{}'".format(
        x[0]['name'].split('.')[0], x[0]['name'].split('.')[1])
    client.separator = " "
    client.run()
