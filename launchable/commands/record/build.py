import re
import click
import subprocess
import os
from .commit import commit
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.http_client import LaunchableClient
from ...utils.session import clean_session_files


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
@click.option('--max-days',
    help="the maximum number of days to collect commits retroactively",
    default=30
)
@click.option('--no-submodules',
    is_flag=True,
    help="stop collecting information from Git Submodules",
    default=False
)
@click.pass_context
def build(ctx, build_name, source, max_days, no_submodules):
    clean_session_files(days_ago=14)

    # This command accepts REPO_NAME=REPO_DIST and REPO_DIST
    repos = [s.split('=') if re.match(r'[^=]+=[^=]+', s) else (s, s)
             for s in source]
    # TODO: if repo_dist is absolute path, warn the user that that's probably not what they want to do

    for (name, repo_dist) in repos:
        ctx.invoke(commit, source=repo_dist, max_days=max_days)

    sources = [(
        name,
        subprocess.check_output(
            "git rev-parse HEAD".split(), cwd=repo_dist
        ).decode().replace("\n", "")
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
                    hash = matched.group('hash')
                    name = matched.group('name')
                    if hash and name:
                        submodules.append((repo_name + "/" + name, hash))

    # Note: currently becomes unique command args and submodules by the hash.
    # But they can be conflict between repositories.
    uniq_submodules = {hash: (name, hash)
                       for name, hash in sources + submodules}.values()

    try:
        commitHashes = [{
            'repositoryName': name,
            'commitHash': hash
        } for name, hash in uniq_submodules]

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
