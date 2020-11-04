import os
import click
from ...utils.ingester_image import ingester_image
from ...utils.ingester_jar import ingester_jar_url, ingester_jar_version
import subprocess
import requests
import pathlib
import sys


jar_dir_path = os.path.expanduser(
    "~/.launchable/jar/ingester/{}".format(ingester_jar_version))
jar_file_path = jar_dir_path + "/exe_deploy.jar"


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
        download_jar()
        exec_jar(source)
    elif executable == 'docker':
        exec_docker(source)


def download_jar():
    pathlib.Path(jar_dir_path).mkdir(parents=True, exist_ok=True)

    res = requests.get(ingester_jar_url, stream=True)
    total_length = int(res.headers.get('content-length'))

    if os.path.exists(jar_file_path) and os.path.getsize(jar_file_path) == total_length:
        print("exe_deploy.jar exists in {}".format(jar_dir_path))
    else:
        total_downloaded = 0
        f = open(jar_file_path, 'wb')
        for chunk in res.iter_content(chunk_size=512 * 1024):
            if chunk:
                f.write(chunk)

                total_downloaded += len(chunk)
                sys.stdout.write("\rDownloading exe_deploy.jar: {:.1f}% ({:,} / {:,} byte)".format(
                    (total_downloaded / total_length) * 100,
                    total_downloaded,
                    total_length
                ))
                sys.stdout.flush()

        f.close()
        print("exe_deploy.jar is downloaded in {}".format(jar_dir_path))


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
