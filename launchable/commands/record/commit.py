import os
import click
import sys
from urllib.parse import urlparse

from launchable.utils import subprocess

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
        sys.exit("--executable docker is no longer supported")

    try:
        exec_jar(os.path.abspath(source), max_days, ctx.obj.dry_run)
    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            click.echo(click.style("Can't get commit history from `{}`. Do you run command root of git-controlled directory? If not, please set a directory use by --source option.".format(
                os.path.abspath(source)), fg='yellow'), err=True)
            print(e)


def exec_jar(source, max_days, dry_run):
    java = get_java_command()

    if not java:
        sys.exit("You need to install Java")

    base_url = get_base_url()

    https_proxy = os.getenv("HTTPS_PROXY")
    proxy_option = _build_proxy_option(https_proxy) if https_proxy else ""

    subprocess.check_output("{java} {proxy_option} -jar \"{jar_file_path}\" ingest:commit -endpoint {endpoint} -max-days {max_days} {audit} {scrub_pli} {dry_run} {source}"
                            .format(
                                java=java,
                                proxy_option=proxy_option,
                                jar_file_path=jar_file_path,
                                endpoint="{}/intake/".format(base_url),
                                max_days=max_days,
                                audit="-audit" if Logger().logger.isEnabledFor(LOG_LEVEL_AUDIT) else "",
                                scrub_pli="-scrub-pii",
                                dry_run="-dry-run" if dry_run else "",
                                source=source),
                            shell=True)


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
