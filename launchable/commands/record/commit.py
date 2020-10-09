from ...utils.token import parse_token
import os
import click

@click.command()
@click.option('--source', help="repository path", default="$(pwd)", type=str)
def commit(source):
  token, org, workspace = parse_token()
  os.system("docker run -u $(id -u) -i --rm -v {}:{} --env LAUNCHABLE_TOKEN launchableinc/ingester:latest ingest:commit {}".format(source ,source, source))

