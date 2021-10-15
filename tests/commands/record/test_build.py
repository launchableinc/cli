import json
import os
from unittest import mock

import responses

from tests.cli_test_case import CliTestCase


class BuildTest(CliTestCase):
    # make sure the output of git-submodule is properly parsed
    @responses.activate
    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": CliTestCase.launchable_token})
    @mock.patch('launchable.utils.subprocess.check_output')
    def test_submodule(self, mock_check_output):
        mock_check_output.side_effect = [
            # the first call is git rev-parse HEAD
            ('c50f5de0f06fe16afa4fd1dd615e4903e40b42a2').encode(),
            # the second call is git submodule status --recursive
            (
                ' 491e03096e2234dab9a9533da714fb6eff5dcaa7 foo (v1.51.0-560-g491e030)\n'
                ' 8bccab48338219e73c3118ad71c8c98fbd32a4be bar-zot (v1.32.0-516-g8bccab4)\n'
            ).encode()
        ]
        result = self.cli("record", "build",
                          "--no-commit-collection", "--name", self.build_name)
        self.assertEqual(result.exit_code, 0)

        # Name & Path should both reflect the submodule path
        self.assertTrue(
            "| ./bar-zot | ./bar-zot | 8bccab48338219e73c3118ad71c8c98fbd32a4be |" in result.stdout)

        payload = json.loads(responses.calls[0].request.body.decode())
        self.assert_json_orderless_equal(
            {
                "buildNumber": "123",
                "commitHashes": [
                    {
                        "repositoryName": ".",
                        "commitHash": "c50f5de0f06fe16afa4fd1dd615e4903e40b42a2"
                    },
                    {
                        "repositoryName": "./foo",
                        "commitHash": "491e03096e2234dab9a9533da714fb6eff5dcaa7"
                    },
                    {
                        "repositoryName": "./bar-zot",
                        "commitHash": "8bccab48338219e73c3118ad71c8c98fbd32a4be"
                    },
                ]
            }, payload)
