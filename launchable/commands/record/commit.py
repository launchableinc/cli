from ...utils.token import parse_token
import os
import click
from ...utils.ingester_image import ingester_image

@click.command()
@click.option('--source', help="repository path", default=os.getcwd(), type=str)
def commit(source):
  token, org, workspace = parse_token()
  source = os.path.abspath(source)
  os.system("docker run -u $(id -u) -i --rm -v {}:{} --env LAUNCHABLE_TOKEN {} ingest:commit {}".format(source ,source, ingester_image, source))

