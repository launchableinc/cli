import os
import subprocess
import sys
from typing import List, Optional
from urllib.parse import urlparse

import click

from ...utils.commit_ingester import upload_commits
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.git_log_parser import parse_git_log
from ...utils.http_client import get_base_url
from ...utils.java import cygpath, get_java_command
from ...utils.logger import LOG_LEVEL_AUDIT, Logger

jar_file_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../jar/exe_deploy.jar"))


@click.command()
@click.option(
    '--source',
    help="repository path",
    default=os.getcwd(),
    type=click.Path(exists=True, file_okay=False),
)
@click.option(
    '--executable',
    help="[Obsolete] it was to specify how to perform commit collection but has been removed",
    type=click.Choice(['jar', 'docker']),
    default='jar',
    hidden=True)
@click.option(
    '--max-days',
    help="the maximum number of days to collect commits retroactively",
    default=30)
@click.option(
    '--scrub-pii',
    is_flag=True,
    help='[Deprecated] Scrub emails and names',
    hidden=True)
@click.option(
    '--import-git-log-output',
    help="import from the git-log output",
    type=click.Path(exists=True, dir_okay=False,
                    resolve_path=True, allow_dash=True),
)
@click.pass_context
def commit(ctx, source: str, executable: bool, max_days: int, scrub_pii: bool, import_git_log_output: str):
    if executable == 'docker':
        sys.exit("--executable docker is no longer supported")

    if import_git_log_output:
        _import_git_log(import_git_log_output, ctx.obj.dry_run)
        return

    try:
        exec_jar(os.path.abspath(source), max_days, ctx.obj.dry_run)
    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            click.echo(click.style(
                "Can't get commit history from `{}`. Do you run command root of git-controlled directory? "
                "If not, please set a directory use by --source option."
                .format(os.path.abspath(source)),
                fg='yellow'),
                err=True)
            print(e)


def exec_jar(source: str, max_days: int, dry_run: bool):
    java = get_java_command()

    if not java:
        sys.exit("You need to install Java")

    base_url = get_base_url()

    # using subprocess.check_out with shell=False and a list of command to prevent vulnerability
    # https://knowledge-base.secureflag.com/vulnerabilities/code_injection/os_command_injection_python.html
    command = [java]
    command.extend(_build_proxy_option(os.getenv("HTTPS_PROXY")))
    command.extend([
        "-jar",
        cygpath(jar_file_path),
        "ingest:commit",
        "-endpoint",
        "{}/intake/".format(base_url),
        "-max-days",
        str(max_days),
        "-scrub-pii",
    ])

    if Logger().logger.isEnabledFor(LOG_LEVEL_AUDIT):
        command.append("-audit")
    if dry_run:
        command.append("-dry-run")
    command.append(cygpath(source))

    subprocess.run(
        command,
        check=True,
        shell=False,
    )


def _import_git_log(output_file: str, dry_run: bool):
    try:
        with click.open_file(output_file) as fp:
            commits = parse_git_log(fp)
        upload_commits(commits, dry_run)
    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            click.echo(
                click.style("Failed to import the git-log output", fg='yellow'),
                err=True)
            print(e)


def _build_proxy_option(https_proxy: Optional[str]) -> List[str]:
    if not https_proxy:
        return []

    if not (https_proxy.startswith("https://") or https_proxy.startswith("http://")):
        https_proxy = "https://" + https_proxy
    proxy_url = urlparse(https_proxy)

    options = []
    if proxy_url.hostname:
        options.append("-Dhttps.proxyHost={}".format(proxy_url.hostname))
    if proxy_url.port:
        options.append("-Dhttps.proxyPort={}".format(proxy_url.port))
    return options
