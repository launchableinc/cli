#!/usr/bin/env python3

import urllib.request, json
import os
from dulwich.repo import Repo
import click
import re

from .version import __version__

@click.group()
@click.version_option(version=__version__, prog_name='launchable-cli')
def main():
  pass

@main.group()
def record():
  pass

def _parse_token():
  try:
    token = os.environ["LAUNCHABLE_TOKEN"]
    _, user, _ = token.split(":", 2)
    org, workspace = user.split("/", 1)
  except:
    exit("Please specify valid LAUNCHABLE_TOKEN")
  return token, org, workspace

@record.command()
@click.option('--source', help="repository path", default="$(pwd)", type=str)
def commit(source):
  token, org, workspace = _parse_token()
  os.system("docker run -u $(id -u) -i --rm -v {}:{} --env LAUNCHABLE_TOKEN launchableinc/ingester:latest ingest:commit {}".format(source ,source, source))

@record.command()
@click.option('--name', help='build identifer', required=True, type=str, metavar='BUILD_ID')
@click.option('--source', help='repository name and its commit hash. please specify repoName=hash pair like --source main=./main --source lib=./main/lib', default=["main=."], metavar="REPO_NAME", multiple=True)
def build(name, source):
  token, org, workspace = _parse_token()

  if not all(re.match(r'[^=]+=[^=]+', s) for s in source):
      raise click.BadParameter('--source should be REPO_NAME=REPO_DIST')

  # invoke git directly because dulwich's submodule feature was broken
  submodule_lines = os.popen("git submodule status --recursive").read()
  submodules = [(name, hash) for hash, name, _ in (l.split() for l in submodule_lines.splitlines())]
  sources = [(name, Repo(repo_dist).head().decode('ascii')) for name, repo_dist in (s.split('=') for s in source)]

  # Note: currently becomes unique command args and submodules by the hash. But they can be conflict between repositories.
  uniq_submodules = {hash: (name, hash) for name, hash in sources + submodules}.values()

  try:
    commitHashes = [{
      'repositoryName': name,
      'commitHash': hash
    } for name, hash in uniq_submodules]
    print(commitHashes)

    if not (commitHashes[0]['repositoryName'] and commitHashes[0]['commitHash']):
      exit('Please specify --source as --source .')

    payload = {
      "buildNumber": name,
      "commitHashes": commitHashes
    }

    headers = {
      "Content-Type" : "application/json",
      'Authorization': 'Bearer {}'.format(token)
    }

    url = "https://api.mercury.launchableinc.com/intake/organizations/{}/workspaces/{}/builds".format(org, workspace)

    request = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    with urllib.request.urlopen(request) as response:
      response_body = response.read().decode("utf-8")
      print(response_body)

  except Exception as e:
    print(e)

if __name__ == '__main__':
  main()
