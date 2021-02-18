import os
import click
from urllib.parse import urlparse

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

    https_proxy = os.getenv("HTTPS_PROXY")
    proxy_option = _build_proxy_option(https_proxy) if https_proxy else ""

    os.system(
        "{} {} -jar {} ingest:commit -endpoint {} {}"
        .format(java, proxy_option, jar_file_path, "{}/intake/".format(base_url), source))


def _build_proxy_option(https_proxy: str) -> str:
    if not (https_proxy.startswith("https://") or https_proxy.startswith("http://")):
        https_proxy = "https://" + https_proxy
    proxy_url = urlparse(https_proxy)

    options = []
    if proxy_url.hostname:
        options.append("-Dhttps.proxyHost={}".format(proxy_url.hostname))
    if proxy_url.port:
        options.append("-Dhttps.proxyPort={}".format(proxy_url.port))

    return "{} ".format(" ".join(options)) if len(options) else ""


def exec_docker(source):
    base_url = get_base_url()
    os.system(
        "docker run -u $(id -u) -i --rm "
        "-v {}:{} --env LAUNCHABLE_TOKEN {} ingest:commit -endpoint {} {}"
        .format(source, source, ingester_image, "{}/intake/".format(base_url), source)
    )
