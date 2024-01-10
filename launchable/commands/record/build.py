import os
import re
import sys
from typing import Dict, List, Optional

import click
from tabulate import tabulate

from launchable.utils.key_value_type import normalize_key_value_types
from launchable.utils.link import CIRCLECI_KEY, GITHUB_ACTIONS_KEY, JENKINS_URL_KEY, LinkKind, capture_link
from launchable.utils.tracking import Tracking, TrackingClient

from ...utils import subprocess
from ...utils.authentication import get_org_workspace
from ...utils.click import KeyValueType
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.launchable_client import LaunchableClient
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
@click.option(
    '--branch',
    'branches',
    help="Set repository name and branch name when you use --no-commit-collection option. Please use the same repository name with a commit option",  # noqa: E501
    multiple=True,
    default=[],
    cls=KeyValueType,
)
@click.pass_context
def build(ctx: click.core.Context, build_name: str, source: List[str], max_days: int, no_submodules: bool,
          no_commit_collection: bool, scrub_pii: bool, commits: List[str], links: List[str], branches: List[str]):

    if "/" in build_name or "%2f" in build_name.lower():
        sys.exit("--name must not contain a slash and an encoded slash")
    if "%25" in build_name:
        sys.exit("--name must not contain encoded % (%25)")
    if not no_commit_collection and len(commits) != 0:
        sys.exit("--no-commit-collection must be specified when --commit is used")

    clean_session_files(days_ago=14)

    # Information we want to collect for each Git repository
    # The key data structure throughout the implementation of this command
    class Workspace:
        # identifier given to a Git repository to track the same repository from one 'record build' to next
        name: str
        # path to the Git workspace. Can be None if there's no local workspace present
        dir: str
        # current branch of this workspace
        branch: str
        # SHA1 commit hash that's currently checked out
        commit_hash: str

        def __init__(self, name, dir=None, branch=None, commit_hash=None):
            self.name = name
            self.dir = dir
            self.branch = branch
            self.commit_hash = commit_hash

        def calc_branch_name(self):
            '''
            figure out the branch using the workspace. requires `dir` and `commit_hash` to be set.
            '''

            # Jenkins
            # ref:
            # https://www.theserverside.com/blog/Coffee-Talk-Java-News-Stories-and-Opinions/Complete-Jenkins-Git-environment-variables-list-for-batch-jobs-and-shell-script-builds
            if os.environ.get(JENKINS_URL_KEY):
                self.branch = os.environ.get(JENKINS_GIT_BRANCH_KEY) or os.environ.get(JENKINS_GIT_LOCAL_BRANCH_KEY)

            # Github Actions
            # ref: https://docs.github.com/en/actions/learn-github-actions/variables#default-environment-variables
            if os.environ.get(GITHUB_ACTIONS_KEY):
                self.branch = os.environ.get(GITHUB_ACTIONS_GITHUB_HEAD_REF_KEY) or \
                    os.environ.get(GITHUB_ACTIONS_GITHUB_BASE_REF_KEY)

            # CircleCI
            # ref: https://circleci.com/docs/variables/
            if os.environ.get(CIRCLECI_KEY):
                self.branch = os.environ.get(CIRCLECI_CIRCLE_BRANCH_KEY)
            # AWS CodeBuild
            # ref: https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html
            if os.environ.get(CODE_BUILD_BUILD_ID_KEY):
                v = os.environ.get(CODE_BUILD_WEBHOOK_HEAD_REF_KEY)
                if v:
                    # refs/head/<branch name>
                    self.branch = v.split("/")[-1]

            if self.branch:
                return      # if we've figured this out, great

            try:
                show_ref = subprocess.check_output(["git", "show-ref"], cwd=self.dir).decode()
                refs = [ref for ref in show_ref.split("\n") if self.commit_hash in ref]

                if len(refs) > 0:
                    # e.g) ed6de84bde58d51deebe90e01ddfa5fa78899b1c refs/heads/branch-name
                    self.branch = refs[0].split("/")[-1]
            except Exception:
                # cannot get branch name by git command
                pass

    # The first order of business is to ascertain what Git repositories we have in the workspace
    def list_sources() -> List[Workspace]:
        # This command accepts REPO_NAME=REPO_DIR as well as just REPO_DIR
        pattern = re.compile(r'[^=]+=[^=]+')
        ws: List[Workspace] = []
        for s in source:
            if pattern.match(s):
                kv = s.split('=')
                ws.append(Workspace(name=kv[0], dir=kv[1]))
            else:
                ws.append(Workspace(name=s, dir=s))
            # TODO: if repo_dir is absolute path, warn the user that that's probably
            # not what they want to do
        return ws

    # `record commit` on each top-level (= non submodule) Git repository
    # `record commit` command processes Git submodule on its own,
    # so we need to do this between list_sources and list_submodules
    def collect_commits():
        if not no_commit_collection:
            for w in ws:
                ctx.invoke(commit, source=w.dir, max_days=max_days, scrub_pii=scrub_pii)
        else:
            click.echo(click.style(
                "Warning: Commit collection is turned off. The commit data must be collected separately.",
                fg='yellow'), err=True)

    # tally up all the submodules, unless we are told not to
    def list_submodules(workspaces: List[Workspace]) -> List[Workspace]:
        if no_submodules:
            return workspaces

        r = workspaces.copy()
        for w in workspaces:
            submodule_pattern = re.compile(r"^[\+\-U ](?P<hash>[a-f0-9]{40}) (?P<name>\S+)")

            # invoke git directly because dulwich's submodule feature was broken
            submodule_stdouts = subprocess.check_output("git submodule status --recursive".split(),
                                                        cwd=w.dir).decode().splitlines()
            for submodule_stdout in submodule_stdouts:
                # the output is e.g.
                # "+bbf213437a65e82dd6dda4391ecc5d598200a6ce sub1 (heads/master)"
                matched = submodule_pattern.search(submodule_stdout)
                if matched:
                    commit_hash = matched.group('hash')
                    name = matched.group('name')
                    if commit_hash and name:
                        r.append(Workspace(
                            name=w.name + "/" + name,
                            dir=w.dir + "/" + name,
                            commit_hash=commit_hash))
        return r

    # figure out the commit hash and branch of those workspaces
    def compute_hash_and_branch(ws: List[Workspace]):
        # figure out w.commit_hash and w.branch
        for w in ws:
            try:
                if not w.commit_hash:
                    w.commit_hash = subprocess.check_output("git rev-parse HEAD".split(), cwd=w.dir).decode().replace("\n", "")
            except Exception as e:
                click.echo(
                    click.style(
                        "Can't get commit hash for {}. Do you run command under git-controlled directory? "
                        "If not, please set a directory use by --source option.".format(w.dir),
                        fg='yellow'),
                    err=True)
                print(e, file=sys.stderr)
                sys.exit(1)
            w.calc_branch_name()

        # Our historical behaviour is to ignore --branch options. In that case, we should reject if that option is present
        # I also think it's OK to allow this option to explicitly let the branch name set, since the inference
        #  of the branch name from the workspace is inherently a little fragile

    # Rely on --commit and --branch to create a list of workspaces, even when there's no local Git workspaces
    def synthesize_workspaces() -> List[Workspace]:
        # workspace by its name
        ws: Dict[str, Workspace] = {}

        commit_pattern = re.compile("[0-9A-Fa-f]{5,40}$")

        branch_name_map = dict(normalize_key_value_types(branches))

        for name, hash in normalize_key_value_types(commits):
            if not commit_pattern.match(hash):
                click.echo(click.style(
                    "{}'s commit hash `{}` is invalid.".format(name, hash),
                    fg="yellow"),
                    err=True)
                sys.exit(1)

            ws[name] = Workspace(name=name, commit_hash=hash, branch=branch_name_map.get(name))

        # make sure no invalid branch name options are given
        for k in branch_name_map:
            if not ws.get(k):
                click.echo(click.style(
                    "Invalid repository name {} in a --branch option. "
                    "Perhaps you missed the corresponding --commit option?".format(k),
                    fg="yellow"),
                    err=True)
                # TODO: is there any reason this is not an error? for now erring on caution
                # sys.exit(1)

        return list(ws.values())

    # send all the data to server and obtain build_id, or none if the service is down, to recover
    def send(ws: List[Workspace]) -> Optional[str]:
        # figure out all the CI links to capture
        def compute_links():
            _links = capture_link(os.environ)
            for k, v in normalize_key_value_types(links):
                _links.append({
                    "title": k,
                    "url": v,
                    "kind": LinkKind.CUSTOM_LINK.name,
                })
            return _links

        tracking_client = TrackingClient(Tracking.Command.RECORD_BUILD, app=ctx.obj)
        try:
            payload = {
                "buildNumber": build_name,
                "commitHashes": [{
                    'repositoryName': w.name,
                    'commitHash': w.commit_hash,
                    'branchName': w.branch or ""
                } for w in ws],
                "links": compute_links()
            }

            client = LaunchableClient(app=ctx.obj, tracking_client=tracking_client)

            res = client.request("post", "builds", payload=payload)
            res.raise_for_status()

            # at this point we've successfully send the data, so it's OK to record this build
            write_build(build_name)

            return res.json().get("id", None)
        except Exception as e:
            tracking_client.send_error_event(
                event_name=Tracking.ErrorEvent.INTERNAL_CLI_ERROR,
                stack_trace=str(e),
            )
            if os.getenv(REPORT_ERROR_KEY):
                raise e
            else:
                print(e)
            return None

    # report what we did to the user to assist diagnostics
    def report(ws: List[Workspace], build_id: str):
        org, workspace = get_org_workspace()
        click.echo(
            "Launchable recorded build {} to workspace {}/{} with commits from {} {}:\n".format(
                build_name,
                org,
                workspace,
                len(ws),
                ("repositories" if len(ws) > 1 else "repository"),
            ),
        )

        header = ["Name", "Path", "HEAD Commit"]
        rows = [[w.name, w.dir, w.commit_hash] for w in ws]
        click.echo(tabulate(rows, header, tablefmt="github"))
        click.echo(
            "\nVisit https://app.launchableinc.com/organizations/{organization}/workspaces/"
            "{workspace}/data/builds/{build_id} to view this build and its test sessions"
            .format(
                organization=org,
                workspace=workspace,
                build_id=build_id,
            ))

    # all the logics at the high level
    if len(commits) == 0:
        ws = list_sources()
        collect_commits()
        ws = list_submodules(ws)
        compute_hash_and_branch(ws)
    else:
        ws = synthesize_workspaces()
    build_id = send(ws)
    if not build_id:
        return  # recover from service outage gracefully
    report(ws, build_id)
