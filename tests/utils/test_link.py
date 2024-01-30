from unittest import TestCase

from launchable.utils.link import LinkKind, capture_link


class LinkTest(TestCase):
    def test_jenkins(self):
        envs = {
            "JENKINS_URL": "https://jenkins.io",
            "BUILD_URL": "https://jenkins.launchableinc.com/build/123",
            "JOB_NAME": "foo",
            "BUILD_DISPLAY_NAME": "#123"
        }
        self.assertEqual(capture_link(envs), [{
            "kind": LinkKind.JENKINS.name,
            "title": "foo #123",
            "url": "https://jenkins.launchableinc.com/build/123",
        }])

    def test_github_actions(self):
        envs = {
            "GITHUB_ACTIONS": "true",
            "GITHUB_SERVER_URL": "https://github.com",
            "GITHUB_REPOSITORY": "launchable/cli",
            "GITHUB_RUN_ID": 123,
            "GITHUB_WORKFLOW": "workflow",
            "GITHUB_JOB": "job",
            "GITHUB_RUN_NUMBER": "234"
        }
        self.assertEqual(capture_link(envs), [{
            "kind": LinkKind.GITHUB_ACTIONS.name,
            "title": "workflow / job #234",
            "url": "https://github.com/launchable/cli/actions/runs/123",
        }])

    def test_circleci(self):
        envs = {
            "CIRCLECI": "true",
            "CIRCLE_BUILD_URL": "https://circleci.com/build/123",
            "CIRCLE_JOB": "job",
            "CIRCLE_BUILD_NUM": "234"}
        self.assertEqual(capture_link(envs), [{
            "kind": LinkKind.CIRCLECI.name,
            "title": "job (234)",
            "url": "https://circleci.com/build/123",
        }])
