from ...utils.token import parse_token
import os
import click
from ...utils.ingester_image import ingester_image
import subprocess


@click.command()
@click.option('--source',
              help="repository path",
              default=os.getcwd(),
              type=str
)
@click.option('--executable',
              help="",
              type=click.Choice(['jar', 'docker']),
              default='jar'
)
def commit(source, executable):
    source = os.path.abspath(source)

    if executable == 'jar':
        exec_jar(source)
    elif executable == 'docker':
        exec_docker(source)


def exec_jar(source):
    res = subprocess.run(["which", "java"], stdout=subprocess.DEVNULL)
    java = None
    if res.returncode == 0:
        java = "java"
    elif os.access(os.path.expandvars("$JAVA_HOME/bin/java"), os.X_OK):
        java = "$JAVA_HOME/bin/java"

    if not java:
        exit("You need to install Java or try --executable docker")

    os.system(
        "{} -jar bin/exe_deploy.jar ingest:commit {}"
        .format(java, source))


def exec_docker(source):
    os.system(
        "docker run -u $(id -u) -i --rm " \
        "-v {}:{} --env LAUNCHABLE_TOKEN {} ingest:commit {}"
        .format(source, source, ingester_image, source)
    )
