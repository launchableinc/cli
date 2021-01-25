import gzip
import json
import os
import unittest
import types
import responses

import click.testing
from click.testing import CliRunner

from launchable.__main__ import main
from launchable.utils.session import clean_session_files
from launchable.utils.http_client import get_base_url


class CliTestCase(unittest.TestCase):
    """
    Base class for setting up test to invoke CLI
    """
    organization = 'launchableinc'
    workspace = 'mothership'
    launchable_token = "v1:{}/{}:auth-token-sample".format(
        organization, workspace)
    session_id = 16
    build_name = 123
    session = "/intake/organizations/{}/workspaces/{}/builds/{}/test_sessions/{}".format(
        organization, workspace, build_name, session_id)

    def setUp(self):
        self.maxDiff = None
        os.environ['LAUNCHABLE_TOKEN'] = self.launchable_token

        responses.add(responses.POST, "{}/intake/organizations/{}/workspaces/{}/builds/{}/test_sessions".format(get_base_url(), self.organization, self.workspace, self.build_name),
                      json={'id': self.session_id}, status=200)
        responses.add(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(get_base_url(), self.organization, self.workspace),
                      json={'testPaths': []}, status=200)

        responses.add(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(get_base_url(), self.organization, self.workspace,),
                      json={'testPaths': []}, status=200)

    def tearDown(self):
        clean_session_files()

    def cli(self, *args, **kwargs) -> click.testing.Result:
        """
        Invoke CLI command and returns its result
        """
        return CliRunner().invoke(main, args, catch_exceptions=False, **kwargs)

    def load_json_from_file(self, file):
        with file.open() as json_file:
            return json.load(json_file)

    def payload(self, mock_post):
        """
        Given a mock request object, capture the payload sent to the server
        """
        for (args, kwargs) in mock_post.call_args_list:
            if kwargs.get('data'):
                data = kwargs['data']
                if isinstance(data, types.GeneratorType):
                    data = b''.join(data)
                return data

        raise Exception("No data posted")

    def gzipped_json_payload(self, mock_post):
        return json.loads(gzip.decompress(self.payload(mock_post)).decode())

    def json_payload(self, mock_post):
        return json.loads(self.payload(mock_post))

    def assert_json_orderless_equal(self, a, b):
        """
        Compare two JSON trees ignoring orders of items in list & dict
        """

        def tree_sorted(obj):
            if isinstance(obj, dict):
                return sorted((k, tree_sorted(v)) for k, v in obj.items())
            if isinstance(obj, list):
                return sorted(tree_sorted(x) for x in obj)
            else:
                return obj

        self.assertEqual(tree_sorted(a), tree_sorted(b))
