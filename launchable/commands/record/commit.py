import os

import click

from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.http_client import get_base_url
from ...utils.ingester_image import ingester_image
from ...utils.java import get_java_command

jar_file_path = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "../../jar/exe_deploy.jar"))


@click.command()
@click.option('--source',
              help="repository path",
              default=os.getcwd(),
              type=click.Path(exists=True, file_okay=False),
              )
@click.option('--executable',
              help="collect commits with Jar or Docker",
              type=click.Choice(['jar', 'docker']),
              default='jar'
              )
def commit(source, executable):
    source = os.path.abspath(source)

    if executable == 'jar':
        try:
            exec_jar(source)
        except Exception as e:
            if os.getenv(REPORT_ERROR_KEY):
                raise e
            else:
                print(e)
    elif executable == 'docker':
        exec_docker(source)


def exec_jar(source):
    java = get_java_command()

    if not java:
        exit("You need to install Java or try --executable docker")

    base_url = get_base_url()
    os.system(
        "{} -jar {} ingest:commit -endpoint {} {}"
        .format(java, jar_file_path, "{}/intake/".format(base_url), source))


def exec_docker(source):
    base_url = get_base_url()
    os.system(
        "docker run -u $(id -u) -i --rm "
        "-v {}:{} --env LAUNCHABLE_TOKEN {} ingest:commit -endpoint {} {}"
        .format(source, source, ingester_image, "{}/intake/".format(base_url), source)
    )
