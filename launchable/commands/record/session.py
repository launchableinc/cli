import click
import os

from ...utils.http_client import LaunchableClient
from ...utils.token import parse_token
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.session import write_session


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
def session(build_name: str, save_session_file: bool, print_session: bool = True):
    """
    print_session is for barckward compatibility.
    If you run this `record session` standalone, the command should print the session ID because v1.1 users expect the beheivior. That is why the flag is default True.
    If you run this command from the other command such as `subset` and `record tests`, you should set print_session = False because users don't expect to print session ID to the subset output.
    """
    token, org, workspace = parse_token()

    headers = {
        "Content-Type": "application/json",
    }

    client = LaunchableClient(token)

    try:
        session_path = "/intake/organizations/{}/workspaces/{}/builds/{}/test_sessions".format(
            org, workspace, build_name)
        res = client.request("post", session_path, headers=headers)
        res.raise_for_status()
        session_id = res.json()['id']

        if save_session_file:
            write_session(build_name, "{}/{}".format(session_path, session_id))
        if print_session:
            # what we print here gets captured and passed to `--session` in later commands
            click.echo("{}/{}".format(session_path, session_id))

    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            click.echo(e, err=True)
