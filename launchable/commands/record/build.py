import re
import click
import subprocess
import urllib.request, json
from ...utils.token import parse_token

@click.command()
@click.option('--name', 'build_number', help='build identifer', required=True, type=str, metavar='BUILD_ID')
@click.option('--source', help='repository name and its commit hash. please specify repoName=hash pair like --source main=./main --source lib=./main/lib', default=["main=."], metavar="REPO_NAME", multiple=True)
def build(build_number, source):
  token, org, workspace = parse_token()

  if not all(re.match(r'[^=]+=[^=]+', s) for s in source):
      raise click.BadParameter('--source should be REPO_NAME=REPO_DIST')

  repos = [s.split('=') for s in source]
  sources = [(name, subprocess.check_output("git rev-parse HEAD".split(), cwd=repo_dist).decode()) for name, repo_dist in repos]
  submodules = []
  for repo_name, repo_dist in repos:
    # invoke git directly because dulwich's submodule feature was broken
    submodule_stdouts = subprocess.check_output("git submodule status --recursive".split(), cwd=repo_dist).decode().splitlines()
    for submodule_stdout in submodule_stdouts:
      # the output is e.g. "+bbf213437a65e82dd6dda4391ecc5d598200a6ce sub1 (heads/master)"
      matched = re.search(r"^[\+\-U ](?P<hash>[a-f0-9]{40}) (?P<name>\w+)", submodule_stdout)
      if matched:
        hash = matched.group('hash')
        name = matched.group('name')        
        if hash and name:
          submodules.append((repo_name+"/"+name, hash))

  # Note: currently becomes unique command args and submodules by the hash. But they can be conflict between repositories.
  uniq_submodules = {hash: (name, hash) for name, hash in sources + submodules}.values()

  try:
    commitHashes = [{
      'repositoryName': name,
      'commitHash': hash
    } for name, hash in uniq_submodules]

    if not (commitHashes[0]['repositoryName'] and commitHashes[0]['commitHash']):
      exit('Please specify --source as --source .')

    payload = {
      "buildNumber": build_number,
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
      print("Sent", payload)
      print(response_body)

  except Exception as e:
    print(e)
