import json
import os
from unittest import mock

import responses  # type: ignore

from tests.cli_test_case import CliTestCase


class BuildTest(CliTestCase):
    # make sure the output of git-submodule is properly parsed
    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    @mock.patch.dict(os.environ, {"GITHUB_ACTIONS": ""})
    @mock.patch('smart_tests.utils.subprocess.check_output')
    # to tests on GitHub Actions
    @mock.patch.dict(os.environ, {"GITHUB_ACTIONS": ""})
    @mock.patch.dict(os.environ, {"GITHUB_PULL_REQUEST_URL": ""})
    def test_submodule(self, mock_check_output):
        mock_check_output.side_effect = [
            # the first call is git submodule status --recursive
            (
                ' 491e03096e2234dab9a9533da714fb6eff5dcaa7 foo (v1.51.0-560-g491e030)\n'
                ' 8bccab48338219e73c3118ad71c8c98fbd32a4be bar-zot (v1.32.0-516-g8bccab4)\n'
            ).encode(),
            # the second call is git rev-parse HEAD for the '.' workspace
            ('c50f5de0f06fe16afa4fd1dd615e4903e40b42a2').encode(),
            # the third call is git show-ref for detect branch name
            ('c50f5de0f06fe16afa4fd1dd615e4903e40b42a2 refs/head/main\nc50f5de0f06fe16afa4fd1dd615e4903e40b42a2 refs/remotes/origin/main\n').encode(),  # noqa: E501
        ]

        result = self.cli(
            "record",
            "build",
            "--no-commit-collection",
            "--build",
            self.build_name,
            "--branch",
            "main",
            "--repo-branch-map",
            ".=main",
            "--repo-branch-map",
            "./foo=main",
            "--repo-branch-map",
            "./bar-zot=main")
        self.assert_success(result)

        # Name & Path should both reflect the submodule path
        self.assertTrue("| ./bar-zot | ./bar-zot | 8bccab48338219e73c3118ad71c8c98fbd32a4be |" in result.stdout, result.stdout)

        payload = json.loads(responses.calls[1].request.body.decode())
        self.assert_json_orderless_equal(
            {
                "buildNumber": "123",
                "lineage": "main",
                "commitHashes": [
                    {
                        "repositoryName": ".",
                        "commitHash": "c50f5de0f06fe16afa4fd1dd615e4903e40b42a2",
                        "branchName": "main"
                    },
                    {
                        "repositoryName": "./foo",
                        "commitHash": "491e03096e2234dab9a9533da714fb6eff5dcaa7",
                        "branchName": "main"
                    },
                    {
                        "repositoryName": "./bar-zot",
                        "commitHash": "8bccab48338219e73c3118ad71c8c98fbd32a4be",
                        "branchName": "main"
                    },
                ],
                "links": [],
                "timestamp": None
            }, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    # to tests on GitHub Actions
    @mock.patch.dict(os.environ, {"GITHUB_ACTIONS": ""})
    @mock.patch.dict(os.environ, {"GITHUB_PULL_REQUEST_URL": ""})
    @mock.patch('smart_tests.utils.subprocess.check_output')
    def test_no_submodule(self, mock_check_output):
        mock_check_output.side_effect = [
            # the call is git rev-parse HEAD
            ('c50f5de0f06fe16afa4fd1dd615e4903e40b42a2').encode(),
        ]

        result = self.cli(
            "record",
            "build",
            "--no-commit-collection",
            "--no-submodules",
            "--build",
            self.build_name,
            "--branch",
            "main",
            "--repo-branch-map",
            ".=main")
        self.assert_success(result)

        payload = json.loads(responses.calls[1].request.body.decode())
        self.assert_json_orderless_equal(
            {
                "buildNumber": "123",
                "lineage": "main",
                "commitHashes": [
                    {
                        "repositoryName": ".",
                        "commitHash": "c50f5de0f06fe16afa4fd1dd615e4903e40b42a2",
                        "branchName": "main"
                    },
                ],
                "links": [],
                "timestamp": None
            }, payload)

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    # to tests on GitHub Actions
    @mock.patch.dict(os.environ, {"GITHUB_ACTIONS": ""})
    @mock.patch.dict(os.environ, {"GITHUB_PULL_REQUEST_URL": ""})
    def test_no_git_directory(self):
        orig_dir = os.getcwd()
        try:
            os.chdir(self.dir)

            self.cli(
                "record",
                "build",
                "--no-commit-collection",
                "--commit",
                ".=c50f5de0f06fe16afa4fd1dd615e4903e40b42a2",
                "--build",
                self.build_name,
                "--branch",
                "main",
                "--repo-branch-map",
                ".=main")

            payload = json.loads(responses.calls[1].request.body.decode())
            self.assert_json_orderless_equal(
                {
                    "buildNumber": "123",
                    "lineage": "main",
                    "commitHashes": [
                        {
                            "repositoryName": ".",
                            "commitHash": "c50f5de0f06fe16afa4fd1dd615e4903e40b42a2",
                            "branchName": "main",
                        },
                    ],
                    "links": [],
                    "timestamp": None
                }, payload)

        finally:
            os.chdir(orig_dir)

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    # to tests on GitHub Actions
    @mock.patch.dict(os.environ, {"GITHUB_ACTIONS": ""})
    @mock.patch.dict(os.environ, {"GITHUB_PULL_REQUEST_URL": ""})
    def test_commit_option_and_build_option(self):
        # case only --commit option
        result = self.cli(
            "record",
            "build",
            "--no-commit-collection",
            "--commit",
            "A=abc12",
            "--build",
            self.build_name,
            "--branch",
            "main",
            "--repo-branch-map",
            "A=main")
        self.assert_success(result)

        payload = json.loads(responses.calls[1].request.body.decode())
        self.assert_json_orderless_equal(
            {
                "buildNumber": "123",
                "lineage": "main",
                "commitHashes": [
                    {
                        "repositoryName": "A",
                        "commitHash": "abc12",
                        "branchName": "main"
                    },
                ],
                "links": [],
                'timestamp': None
            }, payload)
        responses.calls.reset()

        # case --commit option and --branch option
        result = self.cli(
            "record",
            "build",
            "--no-commit-collection",
            "--commit",
            "A=abc12",
            "--branch",
            "feature-xxx",
            "--repo-branch-map",
            "A=feature-xxx",
            "--build",
            self.build_name)
        self.assert_success(result)

        payload = json.loads(responses.calls[1].request.body.decode())
        self.assert_json_orderless_equal(
            {
                "buildNumber": "123",
                "lineage": "feature-xxx",
                "commitHashes": [
                    {
                        "repositoryName": "A",
                        "commitHash": "abc12",
                        "branchName": "feature-xxx"
                    },
                ],
                "links": [],
                "timestamp": None
            }, payload)
        responses.calls.reset()

        # case --commit option and --branch option but another one
        result = self.cli(
            "record",
            "build",
            "--no-commit-collection",
            "--commit",
            "A=abc12",
            "--branch",
            "B=feature-yyy",
            "--name",
            self.build_name)
        self.assert_success(result)

        payload = json.loads(responses.calls[1].request.body.decode())
        self.assert_json_orderless_equal(
            {
                "buildNumber": "123",
                "lineage": None,
                "commitHashes": [
                    {
                        "repositoryName": "A",
                        "commitHash": "abc12",
                        "branchName": ""
                    },
                ],
                "links": [],
                "timestamp": None
            }, payload)
        responses.calls.reset()
        self.assertIn("Invalid repository name B in a --branch option.", result.output)

        # case multiple --commit options and multiple --branch options
        result = self.cli(
            "record",
            "build",
            "--no-commit-collection",
            "--commit",
            "A=abc12",
            "--branch",
            "B=feature-yyy",
            "--commit",
            "B=56cde",
            "--branch",
            "A=feature-xxx",
            "--name",
            self.build_name)
        self.assert_success(result)

        payload = json.loads(responses.calls[1].request.body.decode())
        self.assert_json_orderless_equal(
            {
                "buildNumber": "123",
                "lineage": "feature-xxx",
                "commitHashes": [
                    {
                        "repositoryName": "A",
                        "commitHash": "abc12",
                        "branchName": "feature-xxx"
                    },
                    {
                        "repositoryName": "B",
                        "commitHash": "56cde",
                        "branchName": "feature-yyy"
                    },
                ],
                "links": [],
                "timestamp": None
            }, payload)
        responses.calls.reset()

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_build_name_validation(self):
        result = self.cli(
            "record",
            "build",
            "--no-commit-collection",
            "--build",
            "foo/hoge",
            "--branch",
            "main",
            "--commit",
            "foo=abc123",
            "--repo-branch-map",
            "foo=main")
        self.assert_exit_code(result, 1)

        result = self.cli(
            "record",
            "build",
            "--no-commit-collection",
            "--build",
            "foo%2Fhoge",
            "--branch",
            "main",
            "--commit",
            "foo=abc123",
            "--repo-branch-map",
            "foo=main")
        self.assert_exit_code(result, 1)

# make sure the output of git-submodule is properly parsed
    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    # to tests on GitHub Actions
    @mock.patch.dict(os.environ, {"GITHUB_ACTIONS": ""})
    @mock.patch.dict(os.environ, {"GITHUB_PULL_REQUEST_URL": ""})
    @mock.patch('smart_tests.utils.subprocess.check_output')
    def test_with_timestamp(self, mock_check_output):
        result = self.cli(
            "record",
            "build",
            "--no-commit-collection",
            "--commit",
            "repo=abc12",
            "--build",
            self.build_name,
            "--branch",
            "main",
            "--repo-branch-map",
            "repo=main",
            '--timestamp',
            "2025-01-23 12:34:56Z")
        self.assert_success(result)

        payload = json.loads(responses.calls[1].request.body.decode())
        self.assert_json_orderless_equal(
            {
                "buildNumber": "123",
                "lineage": "main",
                "commitHashes": [
                    {
                        "repositoryName": "repo",
                        "commitHash": "abc12",
                        "branchName": "main"
                    },
                ],
                "links": [],
                "timestamp": "2025-01-23T12:34:56+00:00"
            }, payload)

    def test_repo_branch_map_requires_no_commit_collection(self):
        # Test that --repo-branch-map requires --no-commit-collection
        result = self.cli(
            "record",
            "build",
            "--build",
            self.build_name,
            "--branch",
            "main",
            "--repo-branch-map",
            ".=main")
        self.assert_exit_code(result, 1)
        self.assertIn("--no-commit-collection must be specified when --repo-branch-map is used", result.stdout)
