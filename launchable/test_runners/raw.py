from typing import Generator
import click
import datetime
import dateutil.parser
import json
import urllib.parse

from . import launchable
from ..testpath import TestPath, parse_test_path, unparse_test_path
from ..commands.record.case_event import CaseEvent, CaseEventType


@click.argument('test_path_file', required=True, type=click.File('r'))
@launchable.subset
def subset(client, test_path_file):
    """Subset tests

    TEST_PATH_FILE is a file that contains test paths (e.g.
    "file=a.py#class=classA") one per line. Lines start with a hash ('#') are
    considered as a comment and ignored.
    """
    tps = [s.strip() for s in test_path_file.readlines()]
    for tp_str in tps:
        if not tp_str or tp_str.startswith('#'):
            continue
        try:
            tp = parse_test_path(tp_str)
        except ValueError as e:
            exit(e.args[0])
        client.test_path(tp)

    client.formatter = unparse_test_path
    client.separator = '\n'
    client.run()


split_subset = launchable.CommonSplitSubsetImpls(
    __name__, formatter=unparse_test_path, seperator='\n').split_subset()


@click.argument('test_result_file', required=True, type=click.Path(exists=True))
@launchable.record.tests
def record_tests(client, test_result_file):
    """Record test results

    TEST_RESULT_FILE is a file that contains a JSON document that describes the
    test results.

    ## Example JSON document

    {
      "testCases": [
         {
           "testPath": "file=a.py#class=classA",
           "duration": 42,
           "status": "TEST_PASSED",
           "stdout": "This is stdout",
           "stderr": "This is stderr",
           "createdAt": "2021-10-05T12:34:00"
         }
      ]
    }

    ## JSON schema

    {
      "$id": "https://launchableinc.com/schema/RecordTestInput",
      "$schema": "https://json-schema.org/draft/2020-12/schema",
      "title": "RecordTestInput",
      "description": "The input to record test",
      "type": "object",
      "properties": {
        "testCases": {
          "description": "Result of test cases",
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "testPath": {
                "description": "TestPath for the test",
                "type": "string"
              },
              "duration": {
                "description": "Time taken to finish the test in seconds. If unspecified, assume 0 sec.",
                "type": "number",
                "minimum": 0
              },
              "status": {
                "description": "Test result",
                "type": "string",
                "enum": ["TEST_PASSED", "TEST_FAILED", "TEST_SKIPPED"]
              },
              "stdout": {
                "description": "Standard output of the test. If unspecified, assume empty.",
                "type": "string"
              },
              "stderr": {
                "description": "Standard error of the test. If unspecified, assume empty",
                "type": "string"
              },
              "createdAt": {
                "description": "The timestamp that the test started at. If unspecified, assume the current timestamp that the CLI is invoked.",
                "type": "string",
                "format": "date-time"
              }
            },
            "required": ["testPath", "status"]
          }
        }
      },
      "required": ["testCases"]
    }
    """
    def parse(test_result_file: str) -> Generator[CaseEventType, None, None]:
        with open(test_result_file, 'r') as f:
            doc = json.load(f)
        default_created_at = datetime.datetime.now(
            datetime.timezone.utc).isoformat()
        for case in doc['testCases']:
            test_path = case['testPath']
            status = case['status']
            duration_secs = case['duration'] or 0
            created_at = case['createdAt'] or default_created_at

            # Validation
            parse_test_path(test_path)
            if status not in CaseEvent.STATUS_MAP:
                raise ValueError(
                    "The status of {} should be one of {} (was {})".format(
                        test_path, list(CaseEvent.STATUS_MAP.keys()), status))
            if duration_secs < 0:
                raise ValueError(
                    "The duration of {} should be positive (was {})".format(
                        test_path, duration_secs))
            dateutil.parser.parse(created_at)

            yield CaseEvent.create(
                test_path, duration_secs, CaseEvent.STATUS_MAP[status],
                case['stdout'], case['stderr'], created_at)

    client.report(test_result_file)
    client.parse_func = parse
    client.run()
