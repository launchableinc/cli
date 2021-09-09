import os

from unittest import TestCase, mock
from launchable.utils.authentication import get_org_workspace, authentication_headers


class AuthenticationTest(TestCase):
    @mock.patch.dict(os.environ, {}, clear=True)
    def test_get_org_workspace_no_environment_variables(self):
        org, workspace = get_org_workspace()
        self.assertIsNone(org)
        self.assertIsNone(workspace)

    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": "invalid"})
    def test_get_org_workspace_invalid_LAUNCHABLE_TOKEN(self):
        org, workspace = get_org_workspace()
        self.assertIsNone(org)
        self.assertIsNone(workspace)

    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": "v1:launchableinc/test:token"})
    def test_get_org_workspace_valid_LAUNCHABLE_TOKEN(self):
        org, workspace = get_org_workspace()
        self.assertEqual("launchableinc", org)
        self.assertEqual("test", workspace)

    @mock.patch.dict(os.environ, {"LAUNCHABLE_ORGANIZATION": "launchableinc", "LAUNCHABLE_WORKSPACE": "test"}, clear=True)
    def test_get_org_workspace_LAUNCHABLE_ORGANIZATION_and_LAUNCHABLE_WORKSPACE(self):
        org, workspace = get_org_workspace()
        self.assertEqual("launchableinc", org)
        self.assertEqual("test", workspace)

    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": "v1:token_org/token_wp:token", "LAUNCHABLE_ORGANIZATION": "org",
                                  "LAUNCHABLE_WORKSPACE": "wp"})
    def test_get_org_workspace_LAUNCHABLE_TOKEN_and_LAUNCHABLE_ORGANIZATION_and_LAUNCHABLE_WORKSPACE(self):
        org, workspace = get_org_workspace()
        self.assertEqual("token_org", org)
        self.assertEqual("token_wp", workspace)

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_authentication_headers_empty(self):
        header = authentication_headers()
        self.assertEqual(len(header), 0)

    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": "v1:launchableinc/test:token"})
    def test_authentication_headers_LAUNCHABLE_TOKEN(self):
        header = authentication_headers()
        self.assertEqual(len(header), 1)
        self.assertEqual(header["Authorization"],
                         "Bearer v1:launchableinc/test:token")

    @mock.patch.dict(os.environ,
                     {"GITHUB_ACTIONS": "true", "GITHUB_RUN_ID": "1", "GITHUB_REPOSITORY": "launchableinc/test",
                      "GITHUB_WORKFLOW": "build", "GITHUB_RUN_NUMBER": "1", "GITHUB_EVENT_NAME": "push",
                      "GITHUB_PR_HEAD_SHA": "test0", "GITHUB_SHA": "test1"}, clear=True)
    def test_authentication_headers_GitHub_Actions_with_PR_head(self):
        header = authentication_headers()
        self.assertEqual(len(header), 8)
        self.assertEqual(header["GitHub-Actions"], "true")
        self.assertEqual(header["GitHub-Run-Id"], "1")
        self.assertEqual(header["GitHub-Repository"], "launchableinc/test")
        self.assertEqual(header["GitHub-Workflow"], "build")
        self.assertEqual(header["GitHub-Run-Number"], "1")
        self.assertEqual(header["GitHub-Event-Name"], "push")
        self.assertEqual(header["GitHub-Pr-Head-Sha"], "test0")
        self.assertEqual(header["GitHub-Sha"], "test1")

    @mock.patch.dict(os.environ,
                     {"GITHUB_ACTIONS": "true", "GITHUB_RUN_ID": "1", "GITHUB_REPOSITORY": "launchableinc/test",
                      "GITHUB_WORKFLOW": "build", "GITHUB_RUN_NUMBER": "1", "GITHUB_EVENT_NAME": "push",
                      "GITHUB_SHA": "test"}, clear=True)
    def test_authentication_headers_GitHub_Actions_without_PR_head(self):
        header = authentication_headers()
        self.assertEqual(len(header), 7)
        self.assertEqual(header["GitHub-Actions"], "true")
        self.assertEqual(header["GitHub-Run-Id"], "1")
        self.assertEqual(header["GitHub-Repository"], "launchableinc/test")
        self.assertEqual(header["GitHub-Workflow"], "build")
        self.assertEqual(header["GitHub-Run-Number"], "1")
        self.assertEqual(header["GitHub-Event-Name"], "push")
        self.assertEqual(header["GitHub-Sha"], "test")

    @mock.patch.dict(os.environ,
                     {"LAUNCHABLE_TOKEN": "v1:launchableinc/test:token", "GITHUB_ACTIONS": "true", "GITHUB_RUN_ID": "1",
                      "GITHUB_REPOSITORY": "launchableinc/test", "GITHUB_WORKFLOW": "build", "GITHUB_RUN_NUMBER": "1",
                      "GITHUB_EVENT_NAME": "push", "GITHUB_SHA": "test"}, clear=True)
    def test_authentication_headers_LAUNCHABLE_TOKEN_and_GitHub_Actions(self):
        header = authentication_headers()
        self.assertEqual(len(header), 1)
        self.assertEqual(header["Authorization"],
                         "Bearer v1:launchableinc/test:token")
