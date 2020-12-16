import re
import click
import subprocess
import urllib.request
import json
import os
from ...utils.token import parse_token
from .commit import commit
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.http_client import LaunchableClient


@click.command()
@click.option(
    '--name',
    'build_number',
    help='build identifier',
    required=True,
    type=str,
    metavar='BUILD_ID'
)
@click.option(
    '--source',
    help='repository name and repository district. please specify'
    'REPO_DIST like --source . '
    'or REPO_NAME=REPO_DIST like --source main=./main --source lib=./main/lib',
    default=["."],
    metavar="REPO_NAME",
    multiple=True
)
@click.option('--with-commit/--without-commit', help='', default=True)
@click.pass_context
def build(ctx, build_number, source, with_commit):
    token, org, workspace = parse_token()

    # This command accepts REPO_NAME=REPO_DIST and REPO_DIST
    repos = [s.split('=') if re.match(r'[^=]+=[^=]+', s) else (s, s)
             for s in source]

    if with_commit:
        for (name, repo_dist) in repos:
            ctx.invoke(commit, source=repo_dist)

    sources = [(
        name,
        subprocess.check_output(
            "git rev-parse HEAD".split(), cwd=repo_dist
        ).decode().replace("\n", "")
    ) for name, repo_dist in repos]
    submodules = []
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
                    submodules.append((repo_name+"/"+name, hash))

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
            "buildNumber": build_number,
            "commitHashes": commitHashes
        }

        headers = {
            "Content-Type": "application/json",
        }

        path = "/intake/organizations/{}/workspaces/{}/builds".format(
            org, workspace)

        client = LaunchableClient(token)
        res = client.request("post", path, data=json.dumps(
            payload).encode(), headers=headers)
        print(res.status_code)
        res.raise_for_status()

    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            print(e)
