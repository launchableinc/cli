from unittest import TestCase

from launchable.utils.link import LinkKind, capture_link


class LinkTest(TestCase):
    def test_jenkins(self):
        envs = {"JENKINS_URL": "https://jenkins.io", "BUILD_URL": "https://jenkins.launchableinc.com/build/123"}
        self.assertEqual(capture_link(envs), [{
            "kind": LinkKind.JENKINS.name,
            "title": "",
            "url": "https://jenkins.launchableinc.com/build/123",
        }])

    def test_github_actions(self):
        envs = {
            "GITHUB_ACTIONS": "true",
            "GITHUB_SERVER_URL": "https://github.com",
            "GITHUB_REPOSITORY": "launchable/cli",
            "GITHUB_RUN_ID": 123}
        self.assertEqual(capture_link(envs), [{
            "kind": LinkKind.GITHUB_ACTIONS.name,
            "title": "",
            "url": "https://github.com/launchable/cli/actions/runs/123",
        }])

    def test_circleci(self):
        envs = {"CIRCLECI": "true", "CIRCLE_BUILD_URL": "https://circleci.com/build/123"}
        self.assertEqual(capture_link(envs), [{
            "kind": LinkKind.CIRCLECI.name,
            "title": "",
            "url": "https://circleci.com/build/123",
        }])
