import os
import tempfile
from unittest import mock

import responses  # type: ignore

from launchable.commands.split_subset import (SPLIT_BY_GROUP_REST_GROUPS_FILE_NAME,
                                              SPLIT_BY_GROUP_SUBSET_GROUPS_FILE_NAME, SPLIT_BY_GROUPS_NO_GROUP_NAME)
from launchable.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class SplitSubsetTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_split_subset_with_observation_mode(self):
        pipe = "test_1.py\ntest_2.py\ntest_3.py\ntest_4.py\ntest_5.py\ntest_6.py"
        mock_json_response = {
            "testPaths": [
                [{"type": "file", "name": "test_1.py"}],
                [{"type": "file", "name": "test_3.py"}],

            ],
            "rest": [
                [{"type": "file", "name": "test_5.py"}],

            ],
            "subsettingId": 456,
            "isObservation": False,
        }

        responses.replace(
            responses.POST,
            "{}/intake/organizations/{}/workspaces/{}/subset/{}/slice".format(
                get_base_url(),
                self.organization,
                self.workspace,
                self.subsetting_id),
            json=mock_json_response,
            status=200)

        rest = tempfile.NamedTemporaryFile(delete=False)
        result = self.cli("split-subset", "--subset-id", "subset/456", "--bin", "1/2", "--rest",
                          rest.name, "file", mix_stderr=False, input=pipe)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, "test_1.py\ntest_3.py\n")
        self.assertEqual(rest.read().decode(), os.linesep.join(["test_5.py"]))
        rest.close()
        os.unlink(rest.name)

        mock_json_response["isObservation"] = True
        responses.replace(
            responses.POST,
            "{}/intake/organizations/{}/workspaces/{}/subset/{}/slice".format(
                get_base_url(),
                self.organization,
                self.workspace,
                self.subsetting_id),
            json=mock_json_response,
            status=200)

        observation_mode_rest = tempfile.NamedTemporaryFile(delete=False)
        result = self.cli("split-subset", "--subset-id", "subset/456", "--bin", "1/2", "--rest",
                          observation_mode_rest.name, "file", mix_stderr=False, input=pipe)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, "test_1.py\ntest_3.py\ntest_5.py\n")
        self.assertEqual(observation_mode_rest.read().decode(), "")
        observation_mode_rest.close()
        os.unlink(observation_mode_rest.name)

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_split_subset(self):
        pipe = "test_1.py\ntest_2.py\ntest_3.py\ntest_4.py\ntest_5.py\ntest_6.py"
        mock_json_response = {
            "testPaths": [
                [{"type": "file", "name": "test_1.py"}],
                [{"type": "file", "name": "test_6.py"}],
            ],
            "rest": [],
            "subsettingId": 456,
            "isObservation": False,
        }

        responses.replace(
            responses.POST,
            "{}/intake/organizations/{}/workspaces/{}/subset/{}/slice".format(
                get_base_url(),
                self.organization,
                self.workspace,
                self.subsetting_id),
            json=mock_json_response,
            status=200)

        result = self.cli(
            "split-subset",
            "--subset-id",
            "subset/456",
            "--bin",
            "1/2",
            "file",
            mix_stderr=False,
            input=pipe,
        )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, "test_1.py\ntest_6.py\n")

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_split_by_group_names(self):
        mock_json_response = {
            "subsettingId": self.subsetting_id,
            "isObservation": False,
            "splitGroups": [
                {
                    "groupName": "e2e",
                    "subset": [
                        [{"type": "file", "name": "e2e-aaa.py"}],
                        [{"type": "file", "name": "e2e-bbb.py"}],
                    ],
                    "rest": [
                        [{"type": "file", "name": "e2e-ccc.py"}],
                        [{"type": "file", "name": "e2e-ddd.py"}],
                    ]
                },
                {
                    "groupName": "unit-test",
                    "subset": [],
                    "rest": [
                        [{"type": "file", "name": "unit-test-111.py"}],
                        [{"type": "file", "name": "unit-test-222.py"}],
                    ]
                },
                {
                    "groupName": "nogroup",
                    "subset": [
                        [{"type": "file", "name": "aaa.py"}],
                        [{"type": "file", "name": "bbb.py"}],
                    ],
                    "rest": [
                        [{"type": "file", "name": "111.py"}],
                        [{"type": "file", "name": "222.py"}],
                    ],
                }
            ]
        }

        responses.replace(
            responses.POST,
            "{base_url}/intake/organizations/{organization}/workspaces/{workspace}/subset/{subset_id}/split-by-groups".format(
                base_url=get_base_url(),
                organization=self.organization,
                workspace=self.workspace,
                subset_id=self.subsetting_id,
            ),
            json=mock_json_response,
            status=200
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            result = self.cli("split-subset", "--subset-id", "subset/{}".format(self.subsetting_id),
                              "--split-by-groups", "--split-by-groups-output-dir", tmpdir, "file")

            self.assertEqual(result.exit_code, 0)
            with open("{}/subset-e2e.txt".format(tmpdir)) as f:
                self.assertEqual(f.read(), "e2e-aaa.py\ne2e-bbb.py")

            self.assertFalse(os.path.exists("{}/rest-e2e.txt".format(tmpdir)))

            self.assertFalse(os.path.exists("{}/subset-unit-test.txt".format(tmpdir)))

            self.assertFalse(os.path.exists("{}/rest-unit-test.txt".format(tmpdir)))

            with open("{}/subset-{}.txt".format(tmpdir, SPLIT_BY_GROUPS_NO_GROUP_NAME)) as f:
                self.assertEqual(f.read(), "aaa.py\nbbb.py")

            self.assertFalse(os.path.exists("{}/rest-{}.txt".format(tmpdir, SPLIT_BY_GROUPS_NO_GROUP_NAME)))

            with open("{}/{}".format(tmpdir, SPLIT_BY_GROUP_SUBSET_GROUPS_FILE_NAME)) as f:
                self.assertEqual(f.read(), "e2e")

            self.assertFalse(os.path.exists("{}/{}".format(tmpdir, SPLIT_BY_GROUP_REST_GROUPS_FILE_NAME)))

        # with rest option
        with tempfile.TemporaryDirectory() as tmpdir:
            result = self.cli("split-subset", "--subset-id", "subset/{}".format(self.subsetting_id),
                              "--split-by-groups-with-rest", "--split-by-groups-output-dir", tmpdir, "file")

            self.assertEqual(result.exit_code, 0)
            with open("{}/subset-e2e.txt".format(tmpdir)) as f:
                self.assertEqual(f.read(), "e2e-aaa.py\ne2e-bbb.py")

            with open("{}/rest-e2e.txt".format(tmpdir)) as f:
                self.assertEqual(f.read(), "e2e-ccc.py\ne2e-ddd.py")

            self.assertFalse(os.path.exists("{}/subset-unit-test.txt".format(tmpdir)))

            with open("{}/rest-unit-test.txt".format(tmpdir)) as f:
                self.assertEqual(f.read(), "unit-test-111.py\nunit-test-222.py")

            with open("{}/subset-{}.txt".format(tmpdir, SPLIT_BY_GROUPS_NO_GROUP_NAME)) as f:
                self.assertEqual(f.read(), "aaa.py\nbbb.py")

            with open("{}/rest-{}.txt".format(tmpdir, SPLIT_BY_GROUPS_NO_GROUP_NAME)) as f:
                self.assertEqual(f.read(), "111.py\n222.py")

            with open("{}/{}".format(tmpdir, SPLIT_BY_GROUP_SUBSET_GROUPS_FILE_NAME)) as f:
                self.assertEqual(f.read(), "e2e")

            with open("{}/{}".format(tmpdir, SPLIT_BY_GROUP_REST_GROUPS_FILE_NAME)) as f:
                self.assertEqual(f.read(), "unit-test")

    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    def test_split_by_group_names_output_exclusion_rules(self):
        mock_json_response = {
            "subsettingId": self.subsetting_id,
            "isObservation": False,
            "splitGroups": [
                {
                    "groupName": "e2e",
                    "subset": [
                        [{"type": "file", "name": "e2e-aaa.py"}],
                        [{"type": "file", "name": "e2e-bbb.py"}],
                    ],
                    "rest": [
                        [{"type": "file", "name": "e2e-ccc.py"}],
                        [{"type": "file", "name": "e2e-ddd.py"}],
                    ]
                },
                {
                    "groupName": "unit-test",
                    "subset": [],
                    "rest": [
                        [{"type": "file", "name": "unit-test-111.py"}],
                        [{"type": "file", "name": "unit-test-222.py"}],
                    ]
                },
                {
                    "groupName": "nogroup",
                    "subset": [
                        [{"type": "file", "name": "aaa.py"}],
                        [{"type": "file", "name": "bbb.py"}],
                    ],
                    "rest": [
                        [{"type": "file", "name": "111.py"}],
                        [{"type": "file", "name": "222.py"}],
                    ],
                }
            ]
        }

        responses.replace(
            responses.POST,
            "{base_url}/intake/organizations/{organization}/workspaces/{workspace}/subset/{subset_id}/split-by-groups".format(
                base_url=get_base_url(),
                organization=self.organization,
                workspace=self.workspace,
                subset_id=self.subsetting_id,
            ),
            json=mock_json_response,
            status=200
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            result = self.cli("split-subset", "--subset-id", "subset/{}".format(self.subsetting_id),
                              "--split-by-groups", "--split-by-groups-output-dir", tmpdir, '--output-exclusion-rules', "file")

            self.assertEqual(result.exit_code, 0)
            with open("{}/subset-e2e.txt".format(tmpdir)) as f:
                self.assertCountEqual(f.read().splitlines(), ["e2e-ccc.py", "e2e-ddd.py", ])

            self.assertFalse(os.path.exists("{}/rest-e2e.txt".format(tmpdir)))

            with open("{}/subset-unit-test.txt".format(tmpdir)) as f:
                self.assertCountEqual(f.read().splitlines(), ["unit-test-111.py", "unit-test-222.py"])
            self.assertFalse(os.path.exists("{}/rest-unit-test.txt".format(tmpdir)))

            with open("{}/subset-{}.txt".format(tmpdir, SPLIT_BY_GROUPS_NO_GROUP_NAME)) as f:
                self.assertCountEqual(f.read().splitlines(), ["111.py", "222.py"])
            self.assertFalse(os.path.exists("{}/rest-{}.txt".format(tmpdir, SPLIT_BY_GROUPS_NO_GROUP_NAME)))

            with open("{}/{}".format(tmpdir, SPLIT_BY_GROUP_SUBSET_GROUPS_FILE_NAME)) as f:
                self.assertEqual(f.read(), "unit-test")
            self.assertFalse(os.path.exists("{}/{}".format(tmpdir, SPLIT_BY_GROUP_REST_GROUPS_FILE_NAME)))
