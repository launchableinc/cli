import os
import click
from ...utils.ingester_image import ingester_image
from ...utils.ingester_jar import ingester_jar_url, ingester_jar_version
import subprocess
import requests
import pathlib
import sys
import shutil

tmp_dir_path = os.path.expanduser(
    "/tmp/launchable/jar/ingester/{}".format(ingester_jar_version))
tmp_file_path = tmp_dir_path + "/exe_deploy.jar"
jar_dir_path = os.path.expanduser(
    "~/.cache/launchable/jar/ingester/{}".format(ingester_jar_version))
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
        try:
            download_jar()
            exec_jar(source)
        except Exception as e:
            print(e)
    elif executable == 'docker':
        exec_docker(source)


def download_jar():
    if os.path.exists(jar_file_path):
        print("exe_deploy.jar exists in {}".format(jar_dir_path))
    else:
        res = requests.get(ingester_jar_url, stream=True)
        res.raise_for_status()

        total_length = int(res.headers.get('content-length'))
        total_downloaded = 0

        os.makedirs(tmp_dir_path, exist_ok=True)
        f = open(tmp_file_path, 'wb')

        print("Downloading exe_deploy.jar ({:,.2f} MB)".format(
            total_length / (1024 * 1024)))

        for chunk in res.iter_content(chunk_size=1024 * 1024 * 10):
            if chunk:
                f.write(chunk)
                total_downloaded += len(chunk)

                sys.stdout.write("\r{}".format(
                    "." * int(total_downloaded / (1024 * 1024 * 10))
                ))
                sys.stdout.flush()

        f.close()

        os.makedirs(jar_dir_path, exist_ok=True)
        shutil.move(tmp_file_path, jar_dir_path)
        sys.stdout.write(
            "\nexe_deploy.jar is downloaded in {}\n".format(jar_dir_path))


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
