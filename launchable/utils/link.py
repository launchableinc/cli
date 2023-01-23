from enum import Enum
from typing import Dict, List, Mapping

JENKINS_URL_KEY = 'JENKINS_URL'
JENKINS_BUILD_URL_KEY = 'BUILD_URL'
GITHUB_ACTIONS_KEY = 'GITHUB_ACTIONS'
GITHUB_ACTIONS_SERVER_URL_KEY = 'GITHUB_SERVER_URL'
GITHUB_ACTIONS_REPOSITORY_KEY = 'GITHUB_REPOSITORY'
GITHUB_ACTIONS_RUN_ID_KEY = 'GITHUB_RUN_ID'
GITHUB_PULL_REQUEST_URL_KEY = "GITHUB_PULL_REQUEST_URL"
CIRCLECI_KEY = 'CIRCLECI'
CIRCLECI_BUILD_URL_KEY = 'CIRCLE_BUILD_URL'


class LinkKind(Enum):

    LINK_KIND_UNSPECIFIED = 0
    CUSTOM_LINK = 1
    JENKINS = 2
    GITHUB_ACTIONS = 3
    GITHUB_PULL_REQUEST = 4
    CIRCLECI = 5


def capture_link(env: Mapping[str, str]) -> List[Dict[str, str]]:
    links = []

    if env.get(JENKINS_URL_KEY):
        links.append(
            {"kind": LinkKind.JENKINS.name, "url": env.get(JENKINS_BUILD_URL_KEY, ""), "title": ""}
        )
    if env.get(GITHUB_ACTIONS_KEY):
        links.append({
            "kind": LinkKind.GITHUB_ACTIONS.name,
            "url": "{}/{}/actions/runs/{}".format(
                env.get(GITHUB_ACTIONS_SERVER_URL_KEY),
                env.get(GITHUB_ACTIONS_REPOSITORY_KEY),
                env.get(GITHUB_ACTIONS_RUN_ID_KEY),
            ),
            "title": ""
        })
    if env.get(GITHUB_PULL_REQUEST_URL_KEY):
        links.append({
            "kind": LinkKind.GITHUB_PULL_REQUEST.name,
            "url": env.get(GITHUB_PULL_REQUEST_URL_KEY, ""),
            "title": ""
        })
    if env.get(CIRCLECI_KEY):
        links.append(
            {"kind": LinkKind.CIRCLECI.name, "url": env.get(CIRCLECI_BUILD_URL_KEY, ""), "title": ""}
        )

    return links
