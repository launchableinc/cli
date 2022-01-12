import gzip
import json
import os
import shutil
import tempfile
import types
import unittest

import click.testing
import responses  # type: ignore
from click.testing import CliRunner

from launchable.__main__ import main
from launchable.utils.http_client import get_base_url
from launchable.utils.session import SESSION_DIR_KEY, clean_session_files


class CliTestCase(unittest.TestCase):
    """
    Base class for setting up test to invoke CLI
    """
    organization = 'launchableinc'
    workspace = 'mothership'
    launchable_token = "v1:{}/{}:auth-token-sample".format(
        organization, workspace)
    session_id = 16
    build_name = "123"
    subsetting_id = 456
    session = "builds/{}/test_sessions/{}".format(build_name, session_id)

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        os.environ[SESSION_DIR_KEY] = self.dir

        self.maxDiff = None

        responses.add(responses.POST, "{}/intake/organizations/{}/workspaces/{}/builds/{}/test_sessions".format(get_base_url(), self.organization, self.workspace, self.build_name),
                      json={'id': self.session_id}, status=200)
        responses.add(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset".format(get_base_url(), self.organization, self.workspace),
                      json={'testPaths': [], 'rest': [], 'subsettingId': 456}, status=200)
        responses.add(responses.POST, "{}/intake/organizations/{}/workspaces/{}/subset/{}/slice".format(get_base_url(), self.organization, self.workspace, self.subsetting_id),
                      json={'testPaths': [], 'rest': [], 'subsettingId': 456}, status=200)
        responses.add(responses.GET, "{}/intake/organizations/{}/workspaces/{}/subset/{}".format(get_base_url(), self.organization, self.workspace, self.subsetting_id),
                      json={'testPaths': [], 'rest': [], 'subsettingId': 456}, status=200)
        responses.add(responses.POST, "{}/intake/organizations/{}/workspaces/{}/builds/{}/test_sessions/{}/events".format(get_base_url(), self.organization, self.workspace, self.build_name, self.session_id),
                      json={}, status=200)
        responses.add(responses.GET, "{}/intake/organizations/{}/workspaces/{}/test_sessions/{}/events".format(get_base_url(), self.organization, self.workspace, self.session_id),
                      json=[], status=200)
        responses.add(responses.PATCH, "{}/intake/organizations/{}/workspaces/{}/builds/{}/test_sessions/{}/close".format(get_base_url(), self.organization, self.workspace, self.build_name, self.session_id),
                      json={}, status=200)
        responses.add(responses.GET, "{}/intake/organizations/{}/workspaces/{}/builds/{}".format(get_base_url(), self.organization, self.workspace, self.build_name),
                      json={'createdAt': "2020-01-02T03:45:56.123+00:00", 'id': 123}, status=200)

    def tearDown(self):
        clean_session_files()
        del os.environ[SESSION_DIR_KEY]
        shutil.rmtree(self.dir)

    def cli(self, *args, **kwargs) -> click.testing.Result:
        # for CliRunner kwargs
        mix_stderr = True
        if 'mix_stderr' in kwargs:
            mix_stderr = kwargs['mix_stderr']
            del kwargs['mix_stderr']

        """
        Invoke CLI command and returns its result
        """
        return CliRunner(mix_stderr=mix_stderr).invoke(main, args, catch_exceptions=False, **kwargs)

    def load_json_from_file(self, file):
        try:
            with file.open() as json_file:
                return json.load(json_file)
        except Exception as e:
            raise IOError("Failed to parse JSON {}".format(file)) from e

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
