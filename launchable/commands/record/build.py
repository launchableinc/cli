import re
import click
import subprocess
import os
from .commit import commit
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.http_client import LaunchableClient
from ...utils.session import clean_session_files
from tabulate import tabulate
from ...utils.authentication import get_org_workspace


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
@click.pass_context
def build(ctx, build_name, source, max_days, no_submodules,
          no_commit_collection):
    clean_session_files(days_ago=14)

    # This command accepts REPO_NAME=REPO_DIST and REPO_DIST
    repos = [s.split('=') if re.match(r'[^=]+=[^=]+', s) else (s, s)
             for s in source]
    # TODO: if repo_dist is absolute path, warn the user that that's probably not what they want to do

    if no_commit_collection:
        click.echo(click.style(
            "Warning: Commit collection is turned off. The commit data must be collected separately.",
            fg='yellow'), err=True)
    else:
        for (name, repo_dist) in repos:
            ctx.invoke(commit, source=repo_dist, max_days=max_days)

    sources = [(
        name,
        repo_dist,
        subprocess.check_output(
            "git rev-parse HEAD".split(), cwd=repo_dist
        ).decode().replace("\n", ""),
    ) for name, repo_dist in repos]

    submodules = []
    if not no_submodules:
        for repo_name, repo_dist in repos:
            # invoke git directly because dulwich's submodule feature was broken
            submodule_stdouts = subprocess.check_output(
                "git submodule status --recursive".split(), cwd=repo_dist
            ).decode().splitlines()
            for submodule_stdout in submodule_stdouts:
                # the output is e.g.
                # "+bbf213437a65e82dd6dda4391ecc5d598200a6ce sub1 (heads/master)"
                matched = re.search(
                    r"^[\+\-U ](?P<hash>[a-f0-9]{40}) (?P<name>\w+)",
                    submodule_stdout
                )
                if matched:
                    commit_hash = matched.group('hash')
                    name = matched.group('name')
                    if commit_hash and name:
                        submodules.append(
                            (repo_name + "/" + name, repo_dist, commit_hash))

    # Note: currently becomes unique command args and submodules by the hash.
    # But they can be conflict between repositories.
    uniq_submodules = {commit_hash: (name, repo_dist, commit_hash)
                       for name, repo_dist, commit_hash, in sources + submodules}.values()

    try:
        commitHashes = [{
            'repositoryName': name,
            'commitHash': commit_hash
        } for name, _, commit_hash in uniq_submodules]

        if not (commitHashes[0]['repositoryName']
                and commitHashes[0]['commitHash']):
            exit('Please specify --source as --source .')

        payload = {
            "buildNumber": build_name,
            "commitHashes": commitHashes
        }

        client = LaunchableClient()

        res = client.request("post", "builds", payload=payload)
        res.raise_for_status()

    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            print(e)

    org, workspace = get_org_workspace()
    click.echo(
        "Launchable recorded build {} to workspace {}/{} with commits from {} {}\n".format(build_name, org, workspace, len(uniq_submodules), ("repositories" if len(uniq_submodules) > 1 else "repository")))

    header = ["Name", "Path", "HEAD Commit"]
    rows = [[name, repo_dist, commit_hash]
            for name, repo_dist, commit_hash in uniq_submodules]
    click.echo(tabulate(rows, header, tablefmt="github"))
