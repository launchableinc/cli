import glob
import os

import click

from launchable.commands.record.case_event import CaseEvent
from launchable.utils.sax import SaxParser, Element, TagMatcher
from . import launchable
from launchable.testpath import TestPath

# common code between 'subset' & 'record tests' to build up test path from nested <test-suite>s
def build_path(e: Element):
    pp = [] # type: TestPath
    if e.parent:
        pp = e.parent.tags.get('path') or []    # type: ignore
    if e.name == "test-suite":
        # <test-suite>s form a nested tree structure so capture those in path
        e.tags['path'] = pp + [{'type': e.attrs['type'], 'name': e.attrs['name']}]
    if e.name == "test-case":
        e.tags['path'] = pp + [{'type': 'TestCase', 'name': e.attrs['name']}]


@click.argument('report_xml', type=click.Path(exists=True), required=True)
@launchable.subset
def subset(client, report_xml):
    """
    Parse an XML file produced from NUnit --explore option to list up all the viable test cases
    """

    def on_element(e: Element):
        build_path(e)
        if e.name == "test-case":
            client.test_path(e.tags['path'])

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
                    e.tags['path'], # type: ignore
                    float(e.attrs['duration']),
                    CaseEvent.TEST_PASSED if e.attrs['result'] == 'Passed' else CaseEvent.TEST_FAILED,
                    timestamp=str(e.tags['startTime'])))  # timestamp is already iso-8601 formatted

        # the 'start-time' attribute is normally on <test-case> but apparently not always,
        # so we try to use the nearest ancestor as an approximate
        SaxParser([TagMatcher.parse("*/@start-time={startTime}")], on_element).parse(report)

        # return the obtained events as a generator
        return (x for x in events)

    client.parse_func = parse_func
    client.run()
