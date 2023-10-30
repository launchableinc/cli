import glob
import os
from typing import Callable, Dict, List
from xml.etree import ElementTree as ET

import click

from launchable.commands.record.case_event import CaseEvent
from launchable.testpath import TestPath, unparse_test_path, parse_test_path

from . import launchable

# common code between 'subset' & 'record tests' to build up test path from
# nested <test-suite>s

"""
Nested class name handling in .NET
---------------------------------

Nested class 'Zot' in the following example gets the full name "Foo.Bar+Zot":

    namespace Foo {
        class Bar {
            class Zot {
    }}}

This is incontrast to how you refer to this class from the source code. For example,
"new Foo.Bar.Zot()"

The subset command expects the list of tests to be passed to "nunit --testlist" option,
and this option expects test names to be in "Foo.Bar+Zot" format.

"""


def build_path(e: ET.Element, parent: ET.Element):
    pp: TestPath = []
    parent_start_time = parent.attrib.get('start-time')
    if parent_start_time is not None and e.attrib.get('start-time') is None:
        # the 'start-time' attribute is normally on <test-case> but apparently not always,
        # so we try to use the nearest ancestor as an approximate
        e.set('start-time', parent_start_time)
    parent_path = parent.attrib.get('path')
    if parent_path is not None:
        pp = parse_test_path(parent_path)
    if e.tag == "test-suite":
        # <test-suite>s form a nested tree structure so capture those in path
        pp = pp + [{'type': e.attrib['type'], 'name': e.attrib['name']}]
    if e.tag == "test-case":
        # work around a bug in NUnitXML.Logger.
        # see nunit-reporter-bug-with-nested-type.xml test case
        methodname = e.attrib['methodname']
        bra = methodname.find("(")
        idx = methodname.rfind(".", 0, bra)
        if idx >= 0:
            # when things are going well, method name cannot contain '.' since it's not a valid character in a symbol.
            # but when NUnitXML.Logger messes up, it ends up putting the class name and the method name, like
            # <test-case name="TheTest" fullname="Launchable.NUnit.Test.Outer+Inner.TheTest"
            #   methodname="Outer+Inner.TheTest" classname="Test"

            pp = pp[0:-1] + [
                # NUnitXML.Logger mistreats the last portion of the namespace as a test fixture when
                # it really should be test suite. So we patch that up too. This is going beyond what's minimally required
                # to make subset work, because type information won't impact how the test path is printed, but
                # when NUnitXML.Logger eventually fixes this bug, we don't want that to produce different test paths.
                {'type': 'TestSuite', 'name': pp[-1]['name']},
                # Here, we need to insert the missing TestFixture=Outer+Inner.
                # I chose TestFixture because that's what nunit console runner (which we believe is handling it correctly)
                # chooses as its type.
                {'type': 'TestFixture', 'name': methodname[0:idx]}
            ]

        pp = pp + [{'type': 'TestCase', 'name': e.attrib['name']}]

    if len(pp) > 0:
        def split_filepath(path: str) -> List[str]:
            # Supports Linux and Windows
            if '/' in path:
                return path.split('/')
            else:
                return path.split('\\')

        # "Assembly" type contains full path at a customer's environment
        # remove file path prefix in Assembly
        e.set('path', unparse_test_path([
            {**path, 'name': split_filepath(path['name'])[-1]}
            if path['type'] == 'Assembly'
            else path
            for path in pp
        ]))


def nunit_parse_func(report: str):
    events = []

    # parse <test-case> element into CaseEvent
    def on_element(e: ET.Element, parent: ET.Element):
        build_path(e, parent)
        if e.tag == "test-case":
            result = e.attrib.get('result')
            status = CaseEvent.TEST_FAILED
            stderr: List[str] = []
            if result == 'Passed':
                status = CaseEvent.TEST_PASSED
            elif result == 'Skipped':
                status = CaseEvent.TEST_SKIPPED
            else:
                failure = e.find('failure')
                if failure is not None:
                    message = failure.find('message')
                    if message is not None and message.text is not None:
                        stderr.append(message.text)
                    stack_trace = failure.find('stack-trace')
                    if stack_trace is not None and stack_trace.text is not None:
                        stderr.append(stack_trace.text)

            events.append(CaseEvent.create(
                test_path=_replace_fixture_to_suite(e.attrib['path']),  # type: ignore
                duration_secs=float(e.attrib['duration']),
                status=status,
                timestamp=str(e.attrib.get('start-time')),
                stderr='\n'.join(stderr)))  # timestamp is already iso-8601 formatted

    _parse_dfs_element(report=report, on_element=on_element)
    # return the obtained events as a generator
    return (x for x in events)


@click.argument('report_xmls', type=click.Path(exists=True), required=True, nargs=-1)
@launchable.subset
def subset(client, report_xmls):
    """
    Parse an XML file produced from NUnit --explore option to list up all the viable test cases
    """

    def on_element(e: ET.Element, parent: ET.Element):
        build_path(e, parent)
        if e.tag == "test-case":
            client.test_path(_replace_fixture_to_suite(e.attrib['path']))

    for report_xml in report_xmls:
        _parse_dfs_element(report=report_xml, on_element=on_element)

    # join all the names except when the type is ParameterizedMethod, because in that case test cases have
    # the name of the test method in it and ends up creating duplicates
    client.formatter = lambda x: '.'.join([c['name'] for c in x if c['type'] not in ['ParameterizedMethod', 'Assembly']])
    client.run()


split_subset = launchable.CommonSplitSubsetImpls(__name__, formatter=lambda x: '.'.join(
    [c['name'] for c in x if c['type'] not in ['ParameterizedMethod', 'Assembly']])).split_subset()


@click.argument('report_xml', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, report_xml):
    # TODO: copied from ctest -- promote this pattern
    for root in report_xml:
        match = False
        for t in glob.iglob(root, recursive=True):
            match = True
            if os.path.isdir(t):
                client.scan(t, "*.xml")
            else:
                client.report(t)
        if not match:
            click.echo("No matches found: {}".format(root), err=True)

    client.parse_func = nunit_parse_func
    client.run()


"""
    Nunit produces different XML structure report between without --explore option and without it.
    So we replace TestFixture to TestSuite to avid this difference problem.
"""


def _replace_fixture_to_suite(test_path_str: str) -> List[Dict[str, str]]:
    paths = parse_test_path(test_path_str)
    for path in paths:
        if path["type"] == "TestFixture":
            path["type"] = "TestSuite"

    return paths


def _parse_dfs_element(report: str, on_element: Callable[[ET.Element, ET.Element], None]):
    tree = ET.parse(source=report)
    root = tree.getroot()
    stack: List[ET.Element] = [root]
    while len(stack) > 0:
        element = stack.pop()
        for test_suite in element.findall('test-suite') + element.findall('test-case'):
            on_element(test_suite, element)
            stack.append(test_suite)
