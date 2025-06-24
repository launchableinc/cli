import os
import re
import sys
from http import HTTPStatus
from typing import Annotated, List, Optional

import typer

from launchable.utils.link import LinkKind, capture_link
from launchable.utils.tracking import Tracking, TrackingClient

from ...dependency import get_application
from ...utils.launchable_client import LaunchableClient
from ...utils.no_build import NO_BUILD_BUILD_NAME
from ...utils.session import _session_file_path, read_build, write_session
from ...utils.typer_types import validate_datetime_with_tz

LAUNCHABLE_SESSION_DIR_KEY = 'LAUNCHABLE_SESSION_DIR'

app = typer.Typer(name="session", help="Record session information")

TEST_SESSION_NAME_RULE = re.compile("^[a-zA-Z0-9][a-zA-Z0-9_-]*$")


def _validate_session_name(value: str) -> str:
    if value is None:
        return ""

    if TEST_SESSION_NAME_RULE.match(value):
        return value
    else:
        raise typer.BadParameter("--session-name option supports only alphabet(a-z, A-Z), number(0-9), '-', and '_'")


@app.callback(invoke_without_command=True)
def session(
    build_name: Annotated[Optional[str], typer.Option(
        "--build",
        help="build name"
    )] = None,
    save_session_file: Annotated[bool, typer.Option(
        "--save-file/--no-save-file",
        help="save session to file"
    )] = True,
    print_session: bool = True,
    flavor: Annotated[List[str], typer.Option(
        "--flavor",
        help="flavors",
        metavar="KEY=VALUE"
    )] = None,
    is_observation: Annotated[bool, typer.Option(
        "--observation",
        help="enable observation mode"
    )] = False,
    links: Annotated[List[str], typer.Option(
        "--link",
        help="Set external link of title and url"
    )] = None,
    is_no_build: Annotated[bool, typer.Option(
        "--no-build",
        help="If you want to only send test reports, please use this option"
    )] = False,
    session_name: Annotated[Optional[str], typer.Option(
        "--session-name",
        help="test session name"
    )] = None,
    lineage: Annotated[Optional[str], typer.Option(
        help="Set lineage name. A lineage is a set of test sessions grouped and this option value will be used for a "
             "lineage name."
    )] = None,
    test_suite: Annotated[Optional[str], typer.Option(
        "--test-suite",
        help="Set test suite name. A test suite is a collection of test sessions. Setting a test suite allows you to "
             "manage data over test sessions and lineages."
    )] = None,
    timestamp: Annotated[Optional[str], typer.Option(
        help="Used to overwrite the session time when importing historical data. Note: Format must be "
             "`YYYY-MM-DDThh:mm:ssTZD` or `YYYY-MM-DDThh:mm:ss` (local timezone applied)"
    )] = None,
):
    """
    print_session is for backward compatibility.
    If you run this `record session` standalone,
    the command should print the session ID because v1.1 users expect the beheivior.
    That is why the flag is default True.
    If you run this command from the other command such as `subset` and `record tests`,
    you should set print_session = False because users don't expect to print session ID to the subset output.
    """

    # Convert default values for lists
    if flavor is None:
        flavor = []
    if links is None:
        links = []

    # Convert key-value pairs from validation
    flavor_tuples = []
    for kv in flavor:
        if '=' in kv:
            parts = kv.split('=', 1)
            flavor_tuples.append((parts[0].strip(), parts[1].strip()))
        elif ':' in kv:
            parts = kv.split(':', 1)
            flavor_tuples.append((parts[0].strip(), parts[1].strip()))
        else:
            raise typer.BadParameter(f"Expected a key-value pair formatted as --option key=value, but got '{kv}'")

    links_tuples = []
    for kv in links:
        if '=' in kv:
            parts = kv.split('=', 1)
            links_tuples.append((parts[0].strip(), parts[1].strip()))
        elif ':' in kv:
            parts = kv.split(':', 1)
            links_tuples.append((parts[0].strip(), parts[1].strip()))
        else:
            raise typer.BadParameter(f"Expected a key-value pair formatted as --option key=value, but got '{kv}'")

    # Validate session name if provided
    if session_name:
        session_name = _validate_session_name(session_name)

    # Validate and convert timestamp if provided
    if timestamp:
        timestamp = validate_datetime_with_tz(timestamp)

    # Get application context
    app = get_application()

    if not is_no_build and not build_name:
        raise typer.BadParameter("Error: Missing option '--build'")

    if is_no_build:
        build = read_build()
        if build and build != "":
            raise typer.BadParameter(
                "The cli already created '{}'. If you want to use the '--no-build' option, please remove this file "
                "first.".format(_session_file_path()))

        build_name = NO_BUILD_BUILD_NAME

    tracking_client = TrackingClient(Tracking.Command.RECORD_SESSION, app=app)
    client = LaunchableClient(app=app, tracking_client=tracking_client)

    if session_name:
        sub_path = "builds/{}/test_session_names/{}".format(build_name, session_name)
        try:
            res = client.request("get", sub_path)

            if res.status_code != 404:
                msg = "This session name ({}) is already used. Please set another name.".format(session_name)
                typer.secho(msg, fg=typer.colors.RED, err=True)
                tracking_client.send_error_event(
                    event_name=Tracking.ErrorEvent.USER_ERROR,
                    stack_trace=msg,
                )
                sys.exit(2)
        except Exception as e:
            tracking_client.send_error_event(
                event_name=Tracking.ErrorEvent.INTERNAL_CLI_ERROR,
                stack_trace=str(e),
            )
            client.print_exception_and_recover(e)

    flavor_dict = dict(flavor_tuples)

    payload = {
        "flavors": flavor_dict,
        "isObservation": is_observation,
        "noBuild": is_no_build,
        "lineage": lineage,
        "testSuite": test_suite,
        "timestamp": timestamp.isoformat() if timestamp else None,
    }

    _links = capture_link(os.environ)
    for link in links_tuples:
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
            msg = "Build {} was not found." \
                "Make sure to run `launchable record build --name {}` before you run this command.".format(
                    build_name, build_name)
            tracking_client.send_error_event(
                event_name=Tracking.ErrorEvent.INTERNAL_CLI_ERROR,
                stack_trace=msg,
            )
            typer.secho(msg, fg=typer.colors.YELLOW, err=True)
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
            typer.echo("{}/{}".format(sub_path, session_id), nl=False)

    except Exception as e:
        tracking_client.send_error_event(
            event_name=Tracking.ErrorEvent.INTERNAL_CLI_ERROR,
            stack_trace=str(e),
        )
        client.print_exception_and_recover(e)

    if session_name:
        try:
            add_session_name(
                client=client,
                build_name=build_name,
                session_id=session_id,
                session_name=session_name,
            )
        except Exception as e:
            tracking_client.send_error_event(
                event_name=Tracking.ErrorEvent.INTERNAL_CLI_ERROR,
                stack_trace=str(e),
            )
            client.print_exception_and_recover(e)


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
        typer.secho(
            "Test session {} was not found. Record session may have failed.".format(session_id),
            fg=typer.colors.YELLOW, err=True
        )
        sys.exit(1)
    if res.status_code == HTTPStatus.BAD_REQUEST:
        typer.secho(
            "You cannot use test session name {} since it is already used by other test session in your workspace. "
            "The record session is completed successfully without session name.".format(session_name),
            fg=typer.colors.YELLOW, err=True)
        sys.exit(1)

    res.raise_for_status()
