import os
import click
from urllib.parse import urlparse

from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.http_client import get_base_url
from ...utils.java import get_java_command
from ...utils.logger import Logger, LOG_LEVEL_AUDIT

jar_file_path = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "../../jar/exe_deploy.jar"))


@click.command()
@click.option('--source',
              help="repository path",
              default=os.getcwd(),
              type=click.Path(exists=True, file_okay=False),
              )
@click.option('--executable',
              help="[Obsolete] it was to specify how to perform commit collection but has been removed",
              type=click.Choice(['jar', 'docker']),
              default='jar',
              hidden=True
              )
@click.option('--max-days',
              help="the maximum number of days to collect commits retroactively",
              default=30
              )
@click.option('--scrub-pii', is_flag=True, help='[Deprecated] Scrub emails and names', hidden=True)
@click.pass_context
def commit(ctx, source, executable, max_days, scrub_pii):
    if executable == 'docker':
        exit("--executable docker is no longer supported")

    try:
        exec_jar(os.path.abspath(source), max_days, ctx.obj.dry_run)
    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            print(e)


def exec_jar(source, max_days, dry_run):
    java = get_java_command()

    if not java:
        exit("You need to install Java")

    base_url = get_base_url()

    https_proxy = os.getenv("HTTPS_PROXY")
    proxy_option = _build_proxy_option(https_proxy) if https_proxy else ""

    os.system(
        "{} {} -jar \"{}\" ingest:commit -endpoint {} -max-days {} {} {} {} {}"
        .format(java, proxy_option, jar_file_path,
                "{}/intake/".format(base_url), max_days,
                "-audit" if Logger().logger.isEnabledFor(LOG_LEVEL_AUDIT) else "",
                "-scrub-pii",
                "-dry-run" if dry_run else "",
                source))


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
