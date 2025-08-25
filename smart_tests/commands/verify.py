import os
import platform
import re
import subprocess
from typing import List

import typer

from smart_tests.utils.commands import Command
from smart_tests.utils.env_keys import TOKEN_KEY
from smart_tests.utils.tracking import Tracking, TrackingClient

from ..utils.authentication import get_org_workspace
from ..utils.java import get_java_command
from ..utils.launchable_client import LaunchableClient
from ..utils.typer_types import emoji
from ..version import __version__ as version


def compare_version(a: List[int], b: List[int]):
    """Compare two version numbers represented as int arrays"""

    def pick(a, i):
        return a[i] if i < len(a) else 0

    for i in range(max(len(a), len(b))):
        d = pick(a, i) - pick(b, i)
        if d != 0:
            return d  # if they are different, we have the result
    return 0  # identical


def compare_java_version(output: str) -> int:
    """Check if the Java version meets what we need. returns >=0 if we meet the requirement"""
    pattern = re.compile('"([^"]+)"')
    for line in output.splitlines():
        if line.find("java version") != -1:
            # line is like: java version "1.8.0_144"
            m = pattern.search(line)
            if m:
                tokens = m.group(1).split(".")
                if len(tokens) >= 2:
                    versions = [int(x) for x in tokens[0:2]]
                    required = [1, 8]
                    return compare_version(versions, required)
    # couldn't determine, so err on the safe side
    return 0


def check_java_version(javacmd: str) -> int:
    """Check if the Java version meets what we need. returns >=0 if we meet the requirement"""
    try:
        v = subprocess.run([javacmd, "-version"], check=True, stderr=subprocess.PIPE, universal_newlines=True)
        return compare_java_version(v.stderr)
    except subprocess.CalledProcessError:
        return -1


app = typer.Typer(name="verify", help="Verify CLI setup and connectivity")


@app.callback(invoke_without_command=True)
def verify(ctx: typer.Context):
    # Run the verification (no subcommands in this app)
    # In this command, regardless of REPORT_ERROR_KEY, always report an unexpected error with full stack trace
    # to assist troubleshooting. `click.UsageError` is handled by the invoking
    # Click gracefully.

    app_instance = ctx.obj

    org, workspace = get_org_workspace()
    tracking_client = TrackingClient(Command.VERIFY, app=app_instance)
    client = LaunchableClient(tracking_client=tracking_client, app=app_instance)
    java = get_java_command()

    # Print the system information first so that we can get them even if there's
    # an issue.

    typer.echo("Organization: " + repr(org))
    typer.echo("Workspace: " + repr(workspace))
    typer.echo("Proxy: " + repr(os.getenv("HTTPS_PROXY")))
    typer.echo("Platform: " + repr(platform.platform()))
    typer.echo("Python version: " + repr(platform.python_version()))
    typer.echo("Java command: " + repr(java))
    typer.echo("smart-tests version: " + repr(version))

    if org is None or workspace is None:
        msg = (
            "Could not identify Smart Tests organization/workspace. "
            "Please confirm if you set SMART_TESTS_TOKEN or SMART_TESTS_ORGANIZATION and SMART_TESTS_WORKSPACE "
            "environment variables"
        )
        tracking_client.send_error_event(
            event_name=Tracking.ErrorEvent.INTERNAL_CLI_ERROR,
            stack_trace=msg
        )
        typer.secho(msg, fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    try:
        res = client.request("get", "verification")
        if res.status_code == 401:
            if os.getenv(TOKEN_KEY):
                msg = ("Authentication failed. Most likely the value for the SMART_TESTS_TOKEN "
                       "environment variable is invalid.")
            else:
                msg = ("Authentication failed. Please set the SMART_TESTS_TOKEN. "
                       "If you intend to use tokenless authentication, "
                       "kindly reach out to our support team for further assistance.")
            typer.secho(msg, fg=typer.colors.RED, err=True)
            tracking_client.send_error_event(
                event_name=Tracking.ErrorEvent.USER_ERROR,
                stack_trace=msg,
            )
            raise typer.Exit(2)
        res.raise_for_status()
    except Exception as e:
        tracking_client.send_error_event(
            event_name=Tracking.ErrorEvent.INTERNAL_CLI_ERROR,
            stack_trace=str(e),
            api="verification",
        )
        client.print_exception_and_recover(e)

    if java is None:
        msg = "Java is not installed. Install Java version 8 or newer to use the Smart Tests CLI."
        tracking_client.send_error_event(
            event_name=Tracking.ErrorEvent.INTERNAL_CLI_ERROR,
            stack_trace=msg
        )
        typer.secho(msg, fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    # Level 2 check: versions. This is more fragile than just reporting the number, so we move
    # this out here

    if compare_version([int(x) for x in platform.python_version().split('.')], [3, 6]) < 0:
        msg = "Python 3.6 or later is required"
        tracking_client.send_error_event(
            event_name=Tracking.ErrorEvent.INTERNAL_CLI_ERROR,
            stack_trace=msg
        )
        typer.secho(msg, fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    if check_java_version(java) < 0:
        msg = "Java 8 or later is required"
        tracking_client.send_error_event(
            event_name=Tracking.ErrorEvent.INTERNAL_CLI_ERROR,
            stack_trace=msg
        )
        typer.secho(msg, fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    typer.secho("Your CLI configuration is successfully verified" + emoji(" \U0001f389"), fg=typer.colors.GREEN)
