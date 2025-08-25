import os
import subprocess
import sys
from typing import Annotated, List
from urllib.parse import urlparse

import typer

from smart_tests.utils.launchable_client import LaunchableClient
from smart_tests.utils.tracking import Tracking, TrackingClient

from ...app import Application
from ...utils.commands import Command
from ...utils.commit_ingester import upload_commits
from ...utils.env_keys import COMMIT_TIMEOUT, REPORT_ERROR_KEY
from ...utils.fail_fast_mode import set_fail_fast_mode, warn_and_exit_if_fail_fast_mode
from ...utils.git_log_parser import parse_git_log
from ...utils.http_client import get_base_url
from ...utils.java import cygpath, get_java_command
from ...utils.logger import LOG_LEVEL_AUDIT, Logger

jar_file_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../jar/exe_deploy.jar"))


app = typer.Typer(name="commit", help="Record commit information")


@app.callback(invoke_without_command=True)
def commit(
    ctx: typer.Context,
    name: Annotated[str | None, typer.Option(
        help="repository name"
    )] = None,
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
    import_git_log_output: Annotated[str | None, typer.Option(
        help="import from the git-log output"
    )] = None,
):
    app = ctx.obj

    if executable == 'docker':
        typer.echo("--executable docker is no longer supported", err=True)
        raise typer.Exit(1)

    tracking_client = TrackingClient(Command.COMMIT, app=ctx.obj)
    client = LaunchableClient(tracking_client=tracking_client, app=ctx.obj)
    set_fail_fast_mode(client.is_fail_fast_mode())

    if import_git_log_output:
        _import_git_log(import_git_log_output, app)
        return

    # Commit messages are not collected in the default.
    is_collect_message = False
    is_collect_files = False
    try:
        res = client.request("get", "commits/collect/options")
        res.raise_for_status()
        is_collect_message = res.json().get("commitMessage", False)
        is_collect_files = res.json().get("files", False)
    except Exception as e:
        tracking_client.send_error_event(
            event_name=Tracking.ErrorEvent.INTERNAL_CLI_ERROR,
            stack_trace=str(e),
            api="commits/options",
        )
        client.print_exception_and_recover(e)

    cwd = os.path.abspath(source)
    if not name:
        name = os.path.basename(cwd)
    try:
        exec_jar(name, cwd, max_days, ctx.obj, is_collect_message, is_collect_files)
    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            warn_and_exit_if_fail_fast_mode(
                "Couldn't get commit history from `{}`. Do you run command root of git-controlled directory? "
                "If not, please set a directory use by --source option.\nerror: {}".format(cwd, e))


def exec_jar(name: str, source: str, max_days: int, app: Application, is_collect_message: bool, is_collect_files: bool):
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
        "-endpoint",
        f"{base_url}/intake/",
        "-max-days",
        str(max_days)
    ])

    if Logger().logger.isEnabledFor(LOG_LEVEL_AUDIT):
        command.append("-audit")
    if app.dry_run:
        command.append("-dry-run")
    if app.skip_cert_verification:
        command.append("-skip-cert-verification")
    if is_collect_message:
        command.append("-commit-message")
    if is_collect_files:
        command.append("-files")
    if os.getenv(COMMIT_TIMEOUT):
        command.append("-enable-timeout")
    command.append(name)
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
            warn_and_exit_if_fail_fast_mode("Failed to import the git-log output\n error: {}".format(e))


def _build_proxy_option(https_proxy: str | None) -> List[str]:
    if not https_proxy:
        return []

    if not (https_proxy.startswith("https://") or https_proxy.startswith("http://")):
        https_proxy = "https://" + https_proxy
    proxy_url = urlparse(https_proxy)

    options = []
    if proxy_url.hostname:
        options.append(f"-Dhttps.proxyHost={proxy_url.hostname}")
    if proxy_url.port:
        options.append(f"-Dhttps.proxyPort={proxy_url.port}")
    return options
