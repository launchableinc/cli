import os
import subprocess
import sys
from typing import Annotated, List, Optional
from urllib.parse import urlparse

import typer

from launchable.utils.launchable_client import LaunchableClient
from launchable.utils.tracking import Tracking, TrackingClient

from ...app import Application
from ...utils.commit_ingester import upload_commits
from ...utils.env_keys import COMMIT_TIMEOUT, REPORT_ERROR_KEY
from ...utils.git_log_parser import parse_git_log
from ...utils.http_client import get_base_url
from ...utils.java import cygpath, get_java_command
from ...utils.logger import LOG_LEVEL_AUDIT, Logger

jar_file_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../jar/exe_deploy.jar"))


app = typer.Typer(name="commit", help="Record commit information")


@app.callback(invoke_without_command=True)
def commit(
    ctx: typer.Context,
    source: Annotated[str, typer.Option(
        help="repository path"
    )] = os.getcwd(),
    executable: Annotated[str, typer.Option(
        help="[Obsolete] it was to specify how to perform commit collection but has been removed",
        hidden=True
    )] = "jar",
    max_days: Annotated[int, typer.Option(
        help="the maximum number of days to collect commits retroactively"
    )] = 30,
    scrub_pii: Annotated[bool, typer.Option(
        help="[Deprecated] Scrub emails and names",
        hidden=True
    )] = False,
    import_git_log_output: Annotated[Optional[str], typer.Option(
        help="import from the git-log output"
    )] = None,
):
    app = ctx.obj

    if executable == 'docker':
        typer.echo("--executable docker is no longer supported", err=True)
        raise typer.Exit(1)

    if import_git_log_output:
        _import_git_log(import_git_log_output, app)
        return

    tracking_client = TrackingClient(Tracking.Command.COMMIT, app=app)
    client = LaunchableClient(tracking_client=tracking_client, app=app)

    # Commit messages are not collected in the default.
    is_collect_message = False
    try:
        res = client.request("get", "commits/collect/options")
        res.raise_for_status()
        is_collect_message = res.json().get("commitMessage", False)
    except Exception as e:
        tracking_client.send_error_event(
            event_name=Tracking.ErrorEvent.INTERNAL_CLI_ERROR,
            stack_trace=str(e),
            api="commits/options",
        )
        client.print_exception_and_recover(e)

    cwd = os.path.abspath(source)
    try:
        exec_jar(cwd, max_days, app, is_collect_message)
    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            typer.secho(
                "Couldn't get commit history from `{}`. Do you run command root of git-controlled directory? "
                "If not, please set a directory use by --source option."
                .format(cwd),
                fg=typer.colors.YELLOW, err=True)
            print(e)


def exec_jar(source: str, max_days: int, app: Application, is_collect_message: bool):
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
        "-scrub-pii"
    ])

    if Logger().logger.isEnabledFor(LOG_LEVEL_AUDIT):
        command.append("-audit")
    if app.dry_run:
        command.append("-dry-run")
    if app.skip_cert_verification:
        command.append("-skip-cert-verification")
    if is_collect_message:
        command.append("-commit-message")
    if os.getenv(COMMIT_TIMEOUT):
        command.append("-enable-timeout")
    command.append(cygpath(source))

    subprocess.run(
        command,
        check=True,
        shell=False,
    )


def _import_git_log(output_file: str, app: Application):
    try:
        with open(output_file) as fp:
            commits = parse_git_log(fp)
        upload_commits(commits, app)
    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            typer.secho("Failed to import the git-log output", fg=typer.colors.YELLOW, err=True)
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
