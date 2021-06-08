import click
import os
import json
from http import HTTPStatus
from ...utils.http_client import LaunchableClient
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.session import write_session
from ...utils.click import KeyValueType
from ...utils.logger import Logger, AUDIT_LOG_FORMAT

LAUNCHABLE_SESSION_DIR_KEY = 'LAUNCHABLE_SESSION_DIR'


@click.command()
@click.option(
    '--build',
    'build_name',
    help='build name',
    required=True,
    type=str,
    metavar='BUILD_NAME'
)
@click.option(
    '--save-file/--no-save-file',
    'save_session_file',
    help='save session to file',
    default=True,
    metavar='SESSION_FILE'
)
@click.option(
    "--flavor",
    "flavor",
    help='flavors',
    cls=KeyValueType,
    multiple=True,
)
def session(build_name: str, save_session_file: bool, print_session: bool = True, flavor=[]):
    """
    print_session is for barckward compatibility.
    If you run this `record session` standalone, the command should print the session ID because v1.1 users expect the beheivior. That is why the flag is default True.
    If you run this command from the other command such as `subset` and `record tests`, you should set print_session = False because users don't expect to print session ID to the subset output.
    """

    flavor_dict = {}
    for (k, v) in flavor:
        flavor_dict[k] = v

    client = LaunchableClient()
    try:
        sub_path = "builds/{}/test_sessions".format(build_name)
        res = client.request("post", sub_path, payload={"flavors": flavor_dict})

        if res.status_code == HTTPStatus.NOT_FOUND:
            click.echo(click.style(
                "Build {} was not found. Make sure to run `launchable record build --name {}` before".format(build_name, build_name), 'yellow'), err=True)

        res.raise_for_status()
        session_id = res.json()['id']

        if save_session_file:
            write_session(build_name, "{}/{}".format(sub_path, session_id))
        if print_session:
            # what we print here gets captured and passed to `--session` in later commands
            click.echo("{}/{}".format(sub_path, session_id))

    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            click.echo(e, err=True)
