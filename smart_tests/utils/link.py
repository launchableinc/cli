from enum import Enum
from typing import Dict, List, Mapping

JENKINS_URL_KEY = 'JENKINS_URL'
JENKINS_BUILD_URL_KEY = 'BUILD_URL'
JENKINS_BUILD_DISPLAY_NAME_KEY = 'BUILD_DISPLAY_NAME'
JENKINS_JOB_NAME_KEY = 'JOB_NAME'
GITHUB_ACTIONS_KEY = 'GITHUB_ACTIONS'
GITHUB_ACTIONS_SERVER_URL_KEY = 'GITHUB_SERVER_URL'
GITHUB_ACTIONS_REPOSITORY_KEY = 'GITHUB_REPOSITORY'
GITHUB_ACTIONS_RUN_ID_KEY = 'GITHUB_RUN_ID'
GITHUB_ACTIONS_RUN_NUMBER_KEY = 'GITHUB_RUN_NUMBER'
GITHUB_ACTIONS_JOB_KEY = 'GITHUB_JOB'
GITHUB_ACTIONS_WORKFLOW_KEY = 'GITHUB_WORKFLOW'
GITHUB_PULL_REQUEST_URL_KEY = 'GITHUB_PULL_REQUEST_URL'
CIRCLECI_KEY = 'CIRCLECI'
CIRCLECI_BUILD_URL_KEY = 'CIRCLE_BUILD_URL'
CIRCLECI_BUILD_NUM_KEY = 'CIRCLE_BUILD_NUM'
CIRCLECI_JOB_KEY = 'CIRCLE_JOB'


class LinkKind(Enum):

    LINK_KIND_UNSPECIFIED = 0
    CUSTOM_LINK = 1
    JENKINS = 2
    GITHUB_ACTIONS = 3
    GITHUB_PULL_REQUEST = 4
    CIRCLECI = 5


def capture_link(env: Mapping[str, str]) -> List[Dict[str, str]]:
    links = []

    # see https://launchableinc.atlassian.net/wiki/spaces/PRODUCT/pages/612892698/ for the list of
    # environment variables used by various CI systems
    if env.get(JENKINS_URL_KEY):
        links.append({
            "kind": LinkKind.JENKINS.name, "url": env.get(JENKINS_BUILD_URL_KEY, ""),
            "title": "{} {}".format(env.get(JENKINS_JOB_NAME_KEY), env.get(JENKINS_BUILD_DISPLAY_NAME_KEY))
        })
    if env.get(GITHUB_ACTIONS_KEY):
        links.append({
            "kind": LinkKind.GITHUB_ACTIONS.name,
            "url": "{}/{}/actions/runs/{}".format(
                env.get(GITHUB_ACTIONS_SERVER_URL_KEY),
                env.get(GITHUB_ACTIONS_REPOSITORY_KEY),
                env.get(GITHUB_ACTIONS_RUN_ID_KEY),
            ),
            # the nomenclature in GitHub PR comment from GHA has the optional additional part "(a,b,c)" that refers
            # to the matrix, but that doesn't appear to be available as env var. Interestingly, run numbers are not
            # included. Maybe it was seen as too much details and unnecessary for deciding which link to click?
            "title": "{} / {} #{}".format(
                env.get(GITHUB_ACTIONS_WORKFLOW_KEY),
                env.get(GITHUB_ACTIONS_JOB_KEY),
                env.get(GITHUB_ACTIONS_RUN_NUMBER_KEY))
        })
    if env.get(GITHUB_PULL_REQUEST_URL_KEY):
        # TODO: where is this environment variable coming from?
        links.append({
            "kind": LinkKind.GITHUB_PULL_REQUEST.name,
            "url": env.get(GITHUB_PULL_REQUEST_URL_KEY, ""),
            "title": ""
        })
    if env.get(CIRCLECI_KEY):
        # Their UI is organized as "project > branch > workflow > job (buildNum)" and it's not clear to me
        # how much of that information should be present in title.
        links.append({
            "kind": LinkKind.CIRCLECI.name, "url": env.get(CIRCLECI_BUILD_URL_KEY, ""),
            "title": "{} ({})".format(env.get(CIRCLECI_JOB_KEY), env.get(CIRCLECI_BUILD_NUM_KEY))
        })

    return links
