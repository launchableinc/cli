import click
import os
import sys
from typing import Dict, Mapping, Optional, List
from http import HTTPStatus

from ...utils.ci_provider import CIProvider
from ...utils.http_client import LaunchableClient
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.flavor import normalize_flavors
from ...utils.session import write_session
from ...utils.click import KeyValueType

LAUNCHABLE_SESSION_DIR_KEY = 'LAUNCHABLE_SESSION_DIR'

JENKINS_URL_KEY = 'JENKINS_URL'
JENKINS_BUILD_URL_KEY = 'BUILD_URL'
GITHUB_ACTIONS_KEY = 'GITHUB_ACTIONS'
GITHUB_ACTIONS_SERVER_URL_KEY = 'GITHUB_SERVER_URL'
GITHUB_ACTIONS_REPOSITORY_KEY = 'GITHUB_REPOSITORY'
GITHUB_ACTIONS_RUN_ID_KEY = 'GITHUB_RUN_ID'
CIRCLECI_KEY = 'CIRCLECI'
CIRCLECI_BUILD_URL_KEY = 'CIRCLE_BUILD_URL'


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
@click.option(
    "--observation",
    "is_observation",
    help="enable observation mode",
    is_flag=True,
)
@click.pass_context
def session(
    ctx: click.core.Context,
    build_name: str,
    save_session_file: bool,
    print_session: bool = True,
    flavor: List[str] = [],
    is_observation: bool = False,
):
    """
    print_session is for barckward compatibility.
    If you run this `record session` standalone, the command should print the session ID because v1.1 users expect the beheivior. That is why the flag is default True.
    If you run this command from the other command such as `subset` and `record tests`, you should set print_session = False because users don't expect to print session ID to the subset output.
    """

    flavor_dict = {}
    for f in normalize_flavors(flavor):
        flavor_dict[f[0]] = f[1]

    link = _capture_link(os.environ)
    payload = {
        "flavors": flavor_dict,
        "isObservation": is_observation,
    }
    if link:
        payload["link"] = link

    client = LaunchableClient(dry_run=ctx.obj.dry_run)
    try:
        sub_path = "builds/{}/test_sessions".format(build_name)
        res = client.request("post", sub_path, payload=payload)

        if res.status_code == HTTPStatus.NOT_FOUND:
            click.echo(click.style(
                "Build {} was not found. Make sure to run `launchable record build --name {}` before you run this command.".format(
                    build_name,
                    build_name),
                'yellow'),
                err=True,
            )
            sys.exit(1)

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


def _capture_link(env: Mapping[str, str]) -> Optional[Dict[str, str]]:
    if env.get(JENKINS_URL_KEY):
        return {"provider": CIProvider.JENKINS.value, "url": env.get(JENKINS_BUILD_URL_KEY, "")}
    elif env.get(GITHUB_ACTIONS_KEY):
        return {"provider": CIProvider.GITHUB_ACTIONS.value, "url": "{}/{}/actions/runs/{}".format(
            env.get(GITHUB_ACTIONS_SERVER_URL_KEY),
            env.get(GITHUB_ACTIONS_REPOSITORY_KEY),
            env.get(GITHUB_ACTIONS_RUN_ID_KEY),
        ),
        }
    elif env.get(CIRCLECI_KEY):
        return {"provider": CIProvider.CIRCLECI.value, "url": env.get(CIRCLECI_BUILD_URL_KEY, "")}
    else:
        return None
