import glob
import os
from typing import Dict, List

import click

from launchable.commands.record.case_event import CaseEvent
from launchable.utils.sax import SaxParser, Element, TagMatcher
from . import launchable
from launchable.testpath import TestPath

# common code between 'subset' & 'record tests' to build up test path from nested <test-suite>s


def build_path(e: Element):
    pp = []  # type: TestPath
    if e.parent:
        pp = e.parent.tags.get('path') or []    # type: ignore
    if e.name == "test-suite":
        # <test-suite>s form a nested tree structure so capture those in path
        pp = pp + [{'type': e.attrs['type'], 'name': e.attrs['name']}]
    if e.name == "test-case":
        pp = pp + [{'type': 'TestCase', 'name': e.attrs['name']}]

    if len(pp) > 0:
        def split_filepath(path: str) -> List[str]:
            # Supports Linux and Windows
            if '/' in path:
                return path.split('/')
            else:
                return path.split('\\')

        # "Assembly" type containts full path at a cutomer's environment
        # remove file path prefix in Assembly
        e.tags['path'] = [
            {**path, 'name': split_filepath(path['name'])[-1]}
            if path['type'] == 'Assembly'
            else path
            for path in pp
        ]


@click.argument('report_xmls', type=click.Path(exists=True), required=True, nargs=-1)
@launchable.subset
def subset(client, report_xmls):
    """
    Parse an XML file produced from NUnit --explore option to list up all the viable test cases
    """

    def on_element(e: Element):
        build_path(e)
        if e.name == "test-case":
            client.test_path(_replace_fixture_to_suite(
                e.tags['path']))

    for report_xml in report_xmls:
        SaxParser([], on_element).parse(report_xml)

    # join all the names except when the type is ParameterizedMethod, because in that case test cases have
    # the name of the test method in it and ends up creating duplicates
    client.formatter = lambda x: '.'.join(
        [c['name'] for c in x if c['type'] not in ['ParameterizedMethod', 'Assembly']])
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

    def parse_func(report: str):
        events = []

        # parse <test-case> element into CaseEvent
        def on_element(e: Element):
            build_path(e)
            if e.name == "test-case":
                events.append(CaseEvent.create(
                    _replace_fixture_to_suite(e.tags['path']),  # type: ignore
                    float(e.attrs['duration']),
                    CaseEvent.TEST_PASSED if e.attrs['result'] == 'Passed' else CaseEvent.TEST_FAILED,
                    timestamp=str(e.tags['startTime'])))  # timestamp is already iso-8601 formatted

        # the 'start-time' attribute is normally on <test-case> but apparently not always,
        # so we try to use the nearest ancestor as an approximate
        SaxParser(
            [TagMatcher.parse("*/@start-time={startTime}")], on_element).parse(report)

        # return the obtained events as a generator
        return (x for x in events)

    client.parse_func = parse_func
    client.run()


"""
    Nunit produces different XML structure report between without --explore option and without it.
    So we replace TestFixture to TestSuite to avid this difference problem.
"""


def _replace_fixture_to_suite(paths) -> List[Dict[str, str]]:
    for path in paths:
        if path["type"] == "TestFixture":
            path["type"] = "TestSuite"

    return paths
