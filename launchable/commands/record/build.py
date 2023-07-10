import os
import re
import sys
from typing import List

import click
from tabulate import tabulate

from launchable.utils.key_value_type import normalize_key_value_types
from launchable.utils.link import CIRCLECI_KEY, GITHUB_ACTIONS_KEY, JENKINS_URL_KEY, LinkKind, capture_link

from ...utils import subprocess
from ...utils.authentication import get_org_workspace
from ...utils.click import KeyValueType
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.http_client import LaunchableClient
from ...utils.session import clean_session_files, write_build
from .commit import commit

JENKINS_GIT_BRANCH_KEY = "GIT_BRANCH"
JENKINS_GIT_LOCAL_BRANCH_KEY = "GIT_LOCAL_BRANCH"
GITHUB_ACTIONS_GITHUB_HEAD_REF_KEY = "GITHUB_HEAD_REF"
GITHUB_ACTIONS_GITHUB_BASE_REF_KEY = "GITHUB_BASE_REF"
CIRCLECI_CIRCLE_BRANCH_KEY = "CIRCLE_BRANCH"
CODE_BUILD_BUILD_ID_KEY = "CODEBUILD_BUILD_ID"
CODE_BUILD_WEBHOOK_HEAD_REF_KEY = "CODEBUILD_WEBHOOK_HEAD_REF"


@click.command()
@click.option(
    '--name',
    'build_name',
    help='build name',
    required=True,
    type=str,
    metavar='BUILD_NAME'
)
@click.option(
    '--source',
    help='path to local Git workspace, optionally prefixed by a label.  '
    ' like --source path/to/ws or --source main=path/to/ws',
    default=["."],
    metavar="REPO_NAME",
    multiple=True
)
@click.option(
    '--max-days',
    help="the maximum number of days to collect commits retroactively",
    default=30
)
@click.option(
    '--no-submodules',
    is_flag=True,
    help="stop collecting information from Git Submodules",
    default=False
)
@click.option(
    '--no-commit-collection',
    is_flag=True,
    help="""do not collect commit data.

    This is useful if the repository is a shallow clone and the RevWalk is not
    possible. The commit data must be collected with a separate fully-cloned
    repository.
    """,
    default=False
)
@click.option('--scrub-pii', is_flag=True, help='Scrub emails and names', hidden=True)
@click.option(
    '--commit',
    'commits',
    help="set repository name and commit hash when you use --no-commit-collection option",
    multiple=True,
    default=[],
    cls=KeyValueType,
)
@click.option(
    '--link',
    'links',
    help="Set external link of title and url",
    multiple=True,
    default=[],
    cls=KeyValueType,
)
@click.pass_context
def build(ctx: click.core.Context, build_name: str, source: List[str], max_days: int, no_submodules: bool,
          no_commit_collection: bool, scrub_pii: bool, commits: List[str], links: List[str]):

    if "/" in build_name or "%2f" in build_name.lower():
        sys.exit("--name must not contain a slash and an encoded slash")
    if "%25" in build_name:
        sys.exit("--name must not contain encoded % (%25)")
    if not no_commit_collection and len(commits) != 0:
        sys.exit("--no-commit-collection must be specified when --commit is used")

    clean_session_files(days_ago=14)

    # This command accepts REPO_NAME=REPO_DIST and REPO_DIST
    pattern = re.compile(r'[^=]+=[^=]+')
    repos = [s.split('=') if pattern.match(s) else (s, s) for s in source]
    # TODO: if repo_dist is absolute path, warn the user that that's probably
    # not what they want to do

    if no_commit_collection:
        collect_commits = False
        if len(commits) == 0:
            detect_sources = True
            detect_submodules = not no_submodules
        else:
            detect_sources = False
            detect_submodules = False
    else:
        collect_commits = True
        detect_sources = True
        detect_submodules = not no_submodules

    if collect_commits:
        for (name, repo_dist) in repos:
            ctx.invoke(commit, source=repo_dist, max_days=max_days, scrub_pii=scrub_pii)
    else:
        click.echo(click.style(
            "Warning: Commit collection is turned off. The commit data must be collected separately.",
            fg='yellow'), err=True)

    sources = []
    branch_name_map = {}
    if detect_sources:
        try:
            for repo_name, repo_dist in repos:
                hash = subprocess.check_output("git rev-parse HEAD".split(), cwd=repo_dist).decode().replace("\n", "")
                sources.append((repo_name, repo_dist, hash))

                branch_name = _get_branch_name(repo_dist)

                branch_name_map[repo_name] = branch_name

        except Exception as e:
            click.echo(
                click.style(
                    "Can't get commit hash. Do you run command under git-controlled directory? "
                    "If not, please set a directory use by --source option.",
                    fg='yellow'),
                err=True)
            print(e, file=sys.stderr)
            sys.exit(1)

    submodules = []
    if detect_submodules:
        submodule_pattern = re.compile(r"^[\+\-U ](?P<hash>[a-f0-9]{40}) (?P<name>\S+)")
        for repo_name, repo_dist in repos:
            # invoke git directly because dulwich's submodule feature was
            # broken
            submodule_stdouts = subprocess.check_output("git submodule status --recursive".split(),
                                                        cwd=repo_dist).decode().splitlines()
            for submodule_stdout in submodule_stdouts:
                # the output is e.g.
                # "+bbf213437a65e82dd6dda4391ecc5d598200a6ce sub1 (heads/master)"
                matched = submodule_pattern.search(submodule_stdout)
                if matched:
                    commit_hash = matched.group('hash')
                    name = matched.group('name')
                    if commit_hash and name:
                        submodules.append((repo_name + "/" + name, repo_dist + "/" + name, commit_hash))

    if len(commits) != 0:
        invalid = False
        _commits = normalize_key_value_types(commits)

        commit_pattern = re.compile("[0-9A-Fa-f]{5,40}$")
        for repo_name, hash in _commits:
            if not commit_pattern.match(hash):
                click.echo(click.style(
                    "{}'s commit hash `{}` is invalid.".format(repo_name, hash),
                    fg="yellow"),
                    err=True)
                invalid = True
            submodules.append((repo_name, "", hash))
        if invalid:
            sys.exit(1)

    # Note: currently becomes unique command args and submodules by the hash.
    # But they can be conflict between repositories.
    uniq_submodules = {commit_hash: (name, repo_dist, commit_hash)
                       for name, repo_dist, commit_hash, in sources + submodules}.values()

    build_id = None
    try:
        commitHashes = [{
            'repositoryName': name,
            'commitHash': commit_hash,
            'branchName': branch_name_map.get(name, "")
        } for name, _, commit_hash in uniq_submodules]

        if not (commitHashes[0]['repositoryName'] and commitHashes[0]['commitHash']):
            sys.exit('Please specify --source as --source .')

        payload = {
            "buildNumber": build_name,
            "commitHashes": commitHashes,
        }

        _links = capture_link(os.environ)
        if len(links) != 0:
            for link in normalize_key_value_types(links):
                _links.append({
                    "title": link[0],
                    "url": link[1],
                    "kind": LinkKind.CUSTOM_LINK.name,
                })
        payload["links"] = _links

        client = LaunchableClient(dry_run=ctx.obj.dry_run)

        res = client.request("post", "builds", payload=payload)
        res.raise_for_status()

        build_id = res.json().get("id", None)

    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            print(e)
            return

    org, workspace = get_org_workspace()
    click.echo(
        "Launchable recorded build {} to workspace {}/{} with commits from {} {}:\n".format(
            build_name,
            org,
            workspace,
            len(uniq_submodules),
            ("repositories" if len(uniq_submodules) > 1 else "repository"),
        ),
    )

    header = ["Name", "Path", "HEAD Commit"]
    rows = [[name, repo_dist, commit_hash] for name, repo_dist, commit_hash in uniq_submodules]
    click.echo(tabulate(rows, header, tablefmt="github"))
    if build_id:
        click.echo(
            "\nVisit https://app.launchableinc.com/organizations/{organization}/workspaces/"
            "{workspace}/data/builds/{build_id} to view this build and its test sessions"
            .format(
                organization=org,
                workspace=workspace,
                build_id=build_id,
            ))

    write_build(build_name)


def _get_branch_name(repo_dist: str) -> str:

    # Jenkins
    # ref:
    # https://www.theserverside.com/blog/Coffee-Talk-Java-News-Stories-and-Opinions/Complete-Jenkins-Git-environment-variables-list-for-batch-jobs-and-shell-script-builds
    if os.environ.get(JENKINS_URL_KEY):
        if os.environ.get(JENKINS_GIT_BRANCH_KEY):
            return os.environ[JENKINS_GIT_BRANCH_KEY]
        elif os.environ[JENKINS_GIT_LOCAL_BRANCH_KEY]:
            return os.environ[JENKINS_GIT_LOCAL_BRANCH_KEY]
    # Github Actions
    # ref: https://docs.github.com/en/actions/learn-github-actions/variables#default-environment-variables
    if os.environ.get(GITHUB_ACTIONS_KEY):
        if os.environ.get(GITHUB_ACTIONS_GITHUB_HEAD_REF_KEY):
            return os.environ[GITHUB_ACTIONS_GITHUB_HEAD_REF_KEY]
        elif os.environ.get(GITHUB_ACTIONS_GITHUB_BASE_REF_KEY):
            return os.environ[GITHUB_ACTIONS_GITHUB_BASE_REF_KEY]
    # CircleCI
    # ref: https://circleci.com/docs/variables/
    if os.environ.get(CIRCLECI_KEY):
        if os.environ.get(CIRCLECI_CIRCLE_BRANCH_KEY):
            return os.environ[CIRCLECI_CIRCLE_BRANCH_KEY]
    # AWS CodeBuild
    # ref: https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html
    if os.environ.get(CODE_BUILD_BUILD_ID_KEY):
        if os.environ.get(CODE_BUILD_WEBHOOK_HEAD_REF_KEY):
            # refs/head/<branch name>
            return os.environ[CODE_BUILD_WEBHOOK_HEAD_REF_KEY].split("/")[-1]

    branch_name = ""
    try:
        refs = subprocess.check_output(
            "git show-ref | grep '^'$(git rev-parse HEAD)",
            cwd=repo_dist).decode().split("\n")
        if len(refs) > 0:
            # e.g) ed6de84bde58d51deebe90e01ddfa5fa78899b1c refs/heads/branch-name
            branch_name = refs[0].split("/")[-1]
    except Exception:
        # cannot get branch name by git command
        pass
    return branch_name
