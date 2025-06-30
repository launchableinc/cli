from enum import Enum


class CIProvider(Enum):
    JENKINS = "jenkins"
    GITHUB_ACTIONS = "github-actions"
    CIRCLECI = "circleci"
