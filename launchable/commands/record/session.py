import os
import re
import sys
from http import HTTPStatus
from typing import List, Optional

import click

from launchable.utils.key_value_type import normalize_key_value_types
from launchable.utils.link import LinkKind, capture_link

from ...utils.click import KeyValueType
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.http_client import LaunchableClient
from ...utils.no_build import NO_BUILD_BUILD_NAME
from ...utils.session import read_build, write_session

LAUNCHABLE_SESSION_DIR_KEY = 'LAUNCHABLE_SESSION_DIR'

TEST_SESSION_NAME_RULE = re.compile("^[a-zA-Z0-9][a-zA-Z0-9_-]*$")


def _validate_session_name(ctx, param, value):
    if value is None:
        return ""

    if TEST_SESSION_NAME_RULE.match(value):
        return value
    else:
        raise click.BadParameter("--session-name option supports only alphabet(a-z, A-Z), number(0-9), '-', and '_'")


@click.command()
@click.option(
    '--build',
    'build_name',
    help='build name',
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
@click.option(
    "--no-build",
    "is_no_build",
    help="If you want to only send test reports, please use this option",
    is_flag=True,
)
@click.option(
    '--session-name',
    'session_name',
    help='test session name',
    required=False,
    type=str,
    metavar='SESSION_NAME',
    callback=_validate_session_name,
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
    is_no_build: bool = False,
    session_name: Optional[str] = None,
):
    """
    print_session is for backward compatibility.
    If you run this `record session` standalone,
    the command should print the session ID because v1.1 users expect the beheivior.
    That is why the flag is default True.
    If you run this command from the other command such as `subset` and `record tests`,
    you should set print_session = False because users don't expect to print session ID to the subset output.
    """

    if not is_no_build and not build_name:
        raise click.UsageError("Error: Missing option '--build'")

    if is_no_build:
        build = read_build()
        if build and build != "":
            raise click.UsageError(
                'The cli already created `.launchable file`. If you want to use `--no-build option`, please remove `.launchable` file before executing.')  # noqa: E501

        build_name = NO_BUILD_BUILD_NAME

    client = LaunchableClient(dry_run=ctx.obj.dry_run)

    if session_name:
        sub_path = "builds/{}/test_session_names/{}".format(build_name, session_name)
        res = client.request("get", sub_path)

        if res.status_code != 404:
            raise click.UsageError(
                'This session name ({}) is already used. Please set another name.'.format(session_name))

    flavor_dict = {}
    for f in normalize_key_value_types(flavor):
        flavor_dict[f[0]] = f[1]

    payload = {
        "flavors": flavor_dict,
        "isObservation": is_observation,
        "noBuild": is_no_build,
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

        session_id = res.json().get('id', None)
        if is_no_build:
            build_name = res.json().get("buildNumber", "")
            sub_path = "builds/{}/test_sessions".format(build_name)

        if save_session_file:
            write_session(build_name, "{}/{}".format(sub_path, session_id))
        if print_session:
            # what we print here gets captured and passed to `--session` in
            # later commands
            click.echo("{}/{}".format(sub_path, session_id), nl=False)

    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            click.echo(e, err=True)

    if session_name:
        try:
            add_session_name(
                client=client,
                build_name=build_name,
                session_id=session_id,
                session_name=session_name,
            )
        except Exception as e:
            if os.getenv(REPORT_ERROR_KEY):
                raise e
            else:
                click.echo(e, err=True)


def add_session_name(
    client: LaunchableClient,
    build_name: str,
    session_id: str,
    session_name: str,
):
    sub_path = "builds/{}/test_sessions/{}".format(build_name, session_id)
    payload = {
        "name": session_name
    }
    res = client.request("patch", sub_path, payload=payload)

    if res.status_code == HTTPStatus.NOT_FOUND:
        click.echo(
            click.style(
                "Test session {} was not found. Record session may have failed.".format(session_id),
                'yellow'),
            err=True,
        )
        sys.exit(1)
    if res.status_code == HTTPStatus.BAD_REQUEST:
        click.echo(
            click.style(
                "You cannot use test session name {} since it is already used by other test session in your workspace. The record session is completed successfully without session name."  # noqa: E501
                .format(session_name),
                'yellow'),
            err=True,)
        sys.exit(1)

    res.raise_for_status()
