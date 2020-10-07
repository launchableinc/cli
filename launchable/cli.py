#!/usr/bin/env python3

import urllib.request, json
import os
import argparse
from dulwich.repo import Repo

from .version import __version__

def main():
  parser = argparse.ArgumentParser(description='Launchable CLI')
  parser.add_argument('-v', '--version', action='version', version=__version__)
  subparsers = parser.add_subparsers()

  subparsers = subparsers.add_parser('record', help='see `record -h`')

  subsubparsers = subparsers.add_subparsers()

  parser_add = subsubparsers.add_parser('commit', help='see `commit -h`')
  parser_add.add_argument('--path', help="repository path", default="$(pwd)", type=str)
  parser_add.set_defaults(handler=commit)

  parser_add = subsubparsers.add_parser('build', help='see `build -h`')
  parser_add.add_argument('--name', help='build identifer', required=True, type=str, metavar='BUILD_ID')
  parser_add.add_argument('--source', help='repository name and its commit hash. please specify repoName=hash pair like --source . --source ./moduleA', required=True, action='append', metavar="REPO_NAME")
  parser_add.set_defaults(handler=build)

  args = parser.parse_args()
  if hasattr(args, 'handler'):
      args.handler(args)
  else:
      parser.print_help()

def _parse_token():
  try:
    token = os.environ["LAUNCHABLE_TOKEN"]
    _, user, _ = token.split(":", 2)
    org, workspace = user.split("/", 1)
  except:
    exit("Please specify valid LAUNCHABLE_TOKEN")
  return token, org, workspace

def commit(args):
  token, org, workspace = _parse_token()
  path = args.path
  os.system("docker run -u $(id -u) -i --rm -v {}:{} --env LAUNCHABLE_TOKEN launchableinc/ingester:latest ingest:commit {}".format(path,path,path))

def build(args):
  token, org, workspace = _parse_token()
  name = args.name
  sources = args.source
  try:
    commitHashes = [{ 'repositoryName': source, 'commitHash': Repo(source).head().decode('ascii') } for source in sources]
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

    url = "https://api.mercury.launchableinc.com/intake/organizations/{}/workspaces/{}/suts".format(org, workspace)

    request = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    with urllib.request.urlopen(request) as response:
      response_body = response.read().decode("utf-8")
      print(response_body)

  except Exception as e:
    print(e)

if __name__ == '__main__':
  main()
