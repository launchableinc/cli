import os

import click
import platform

from ..utils.env_keys import REPORT_ERROR_KEY
from ..utils.http_client import LaunchableClient
from ..utils.token import parse_token
from ..utils.java import get_java_command

@click.command(name="verify")
def verify():
    try:
        if os.getenv("LAUNCHABLE_TOKEN") is None:
            click.echo(click.style("Could not find the LAUNCHABLE_TOKEN environment variable. Please check if you "
                                   "set it properly.", fg="red"))
            return

        token, org, workspace = parse_token()

        headers = {
            "Content-Type": "application/json",
        }

        path = "/intake/organizations/{}/workspaces/{}/verification".format(
            org, workspace)

        client = LaunchableClient(token)
        res = client.request("get", path, headers=headers)

        if res.status_code == 401:
            click.echo(click.style("Authentication failed. Most likely the value for the LAUNCHABLE_TOKEN "
                                   "environment variable is invalid.", fg="red"))
            return

        res.raise_for_status()

        click.echo("Platform: " + platform.platform())
        click.echo("Python version: " + platform.python_version())

        java = get_java_command()

        if java is None:
            click.echo(click.style(
                "Java is not installed. You need Java to use the Launchable CLI.", fg="red"))
            return

        click.echo("Java command: " + java)

        click.echo(click.style(
            "Your CLI configuration is successfully verified \U0001f389", fg="green"))

    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            print(e)
