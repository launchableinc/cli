import os
import click
from ...utils.ingester_image import ingester_image
import subprocess
from ...utils.env_keys import REPORT_ERROR_KEY

jar_file_path = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "../../jar/exe_deploy.jar"))


@click.command()
@click.option('--source',
              help="repository path",
              default=os.getcwd(),
              type=str
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
    res = subprocess.run(["which", "java"], stdout=subprocess.DEVNULL)
    java = None
    if res.returncode == 0:
        java = "java"
    elif os.access(os.path.expandvars("$JAVA_HOME/bin/java"), os.X_OK):
        java = "$JAVA_HOME/bin/java"

    if not java:
        exit("You need to install Java or try --executable docker")

    os.system(
        "{} -jar {} ingest:commit {}"
        .format(java, jar_file_path, source))


def exec_docker(source):
    os.system(
        "docker run -u $(id -u) -i --rm "
        "-v {}:{} --env LAUNCHABLE_TOKEN {} ingest:commit {}"
        .format(source, source, ingester_image, source)
    )
