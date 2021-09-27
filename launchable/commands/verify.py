import os

import click
import platform
import re
import subprocess
from typing import List

from ..utils.env_keys import REPORT_ERROR_KEY
from ..utils.http_client import LaunchableClient
from ..utils.click import emoji
from ..utils.authentication import get_org_workspace
from ..utils.java import get_java_command
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
    for l in output.splitlines():
        if l.find("java version") != -1:
            # l is like: java version "1.8.0_144"
            m = re.search('"([^"]+)"', l)
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
    v = subprocess.run([javacmd, "-version"], check=True,
                       stderr=subprocess.PIPE, universal_newlines=True)
    return compare_java_version(v.stderr)


@click.command(name="verify")
def verify():
    # In this command, regardless of REPORT_ERROR_KEY, always report an unexpected error with full stack trace
    # to assist troubleshooting. `click.UsageError` is handled by the invoking Click gracefully.

    org, workspace = get_org_workspace()
    client = LaunchableClient()
    java = get_java_command()

    # Print the system information first so that we can get them even if there's
    # an issue.

    click.echo("Organization: " + repr(org))
    click.echo("Workspace: " + repr(workspace))
    click.echo("Proxy: " + repr(os.getenv("HTTPS_PROXY")))
    click.echo("Platform: " + repr(platform.platform()))
    click.echo("Python version: " + repr(platform.python_version()))
    click.echo("Java command: " + repr(java))
    click.echo("launchable version: " + repr(version))

    if org is None or workspace is None:
        raise click.UsageError(click.style(
            "Could not identify Launchable organization/workspace. Please confirm if you set LAUNCHABLE_TOKEN or LAUNCHABLE_ORGANIZATION and LAUNCHABLE_WORKSPACE environment variables",
            fg="red"))

    res = client.request("get", "verification")
    if res.status_code == 401:
        raise click.UsageError(click.style("Authentication failed. Most likely the value for the LAUNCHABLE_TOKEN "
                                           "environment variable is invalid.", fg="red"))
    res.raise_for_status()

    if java is None:
        raise click.UsageError(click.style(
            "Java is not installed. Install Java version 8 or newer to use the Launchable CLI.", fg="red"))

    # Level 2 check: versions. This is more fragile than just reporting the number, so we move
    # this out here

    if compare_version([int(x) for x in platform.python_version().split('.')], [3, 5]) < 0:
        raise click.UsageError(click.style(
            "Python 3.5 or later is required", fg="red"))

    if check_java_version(java) < 0:
        raise click.UsageError(click.style(
            "Java 8 or later is required", fg="red"))

    click.echo(click.style(
        "Your CLI configuration is successfully verified" + emoji(" \U0001f389"), fg="green"))
