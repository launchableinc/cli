import os
import sys
from http import HTTPStatus
from typing import List

import click

from launchable.utils.key_value_type import normalize_key_value_types
from launchable.utils.link import LinkKind, capture_link

from ...utils.click import KeyValueType
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.http_client import LaunchableClient
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
@click.option(
    "--flavor",
    "flavor",
    help='flavors',
    metavar='KEY=VALUE',
    cls=KeyValueType,
    multiple=True,
)
@click.option(
    "--observation",
    "is_observation",
    help="enable observation mode",
    is_flag=True,
)
@click.option(
    '--link',
    'links',
    help="Set external link of title and url",
    multiple=True,
    default=[],
    cls=KeyValueType,
)
@click.pass_context
def session(
    ctx: click.core.Context,
    build_name: str,
    save_session_file: bool,
    print_session: bool = True,
    flavor: List[str] = [],
    is_observation: bool = False,
    links: List[str] = [],
):
    """
    print_session is for barckward compatibility.
    If you run this `record session` standalone,
    the command should print the session ID because v1.1 users expect the beheivior.
    That is why the flag is default True.
    If you run this command from the other command such as `subset` and `record tests`,
    you should set print_session = False because users don't expect to print session ID to the subset output.
    """

    flavor_dict = {}
    for f in normalize_key_value_types(flavor):
        flavor_dict[f[0]] = f[1]

    payload = {
        "flavors": flavor_dict,
        "isObservation": is_observation,
    }

    _links = capture_link(os.environ)
    if len(links) != 0:
        for link in normalize_key_value_types(links):
            _links.append({
                "title": link[0],
                "url": link[1],
                "kind": LinkKind.CUSTOM_LINK.name,
            })
    payload["links"] = _links

    client = LaunchableClient(dry_run=ctx.obj.dry_run)
    try:
        sub_path = "builds/{}/test_sessions".format(build_name)
        res = client.request("post", sub_path, payload=payload)

        if res.status_code == HTTPStatus.NOT_FOUND:
            click.echo(
                click.style(
                    "Build {} was not found. "
                    "Make sure to run `launchable record build --name {}` before you run this command.".format(
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
            # what we print here gets captured and passed to `--session` in
            # later commands
            click.echo("{}/{}".format(sub_path, session_id))

    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            click.echo(e, err=True)
