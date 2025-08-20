import os
import re
import sys
from http import HTTPStatus
from typing import Annotated, List

import typer

from smart_tests.utils.commands import Command
from smart_tests.utils.link import LinkKind, capture_link
from smart_tests.utils.tracking import Tracking, TrackingClient

from ...utils.launchable_client import LaunchableClient
from ...utils.no_build import NO_BUILD_BUILD_NAME
from ...utils.typer_types import validate_datetime_with_tz

app = typer.Typer(name="session", help="Record session information")

TEST_SESSION_NAME_RULE = re.compile("^[a-zA-Z0-9][a-zA-Z0-9_.-]*$")


def _validate_session_name(value: str) -> str:
    if TEST_SESSION_NAME_RULE.match(value):
        return value
    else:
        raise typer.BadParameter("--session option supports only alphabet(a-z, A-Z), number(0-9), '-', '_', and '.'")


@app.callback(invoke_without_command=True)
def session(
    ctx: typer.Context,
    build_name: Annotated[str, typer.Option(
        "--build",
        help="build name"
    )],
    session: Annotated[str, typer.Option(
        "--session",
        help="test session name"
    )],
    test_suite: Annotated[str, typer.Option(
        "--test-suite",
        help="Set test suite name. A test suite is a collection of test sessions. Setting a test suite allows you to "
             "manage data over test sessions and lineages."
    )],
    print_session: bool = True,
    flavor: Annotated[List[str], typer.Option(
        "--flavor",
        help="flavors",
        metavar="KEY=VALUE"
    )] = [],
    is_observation: Annotated[bool, typer.Option(
        "--observation",
        help="enable observation mode"
    )] = False,
    links: Annotated[List[str], typer.Option(
        "--link",
        help="Set external link of title and url"
    )] = [],
    is_no_build: Annotated[bool, typer.Option(
        "--no-build",
        help="If you want to only send test reports, please use this option"
    )] = False,
    timestamp: Annotated[str | None, typer.Option(
        help="Used to overwrite the session time when importing historical data. Note: Format must be "
             "`YYYY-MM-DDThh:mm:ssTZD` or `YYYY-MM-DDThh:mm:ss` (local timezone applied)"
    )] = None,
):

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
    session = _validate_session_name(session)

    # Validate and convert timestamp if provided
    parsed_timestamp = None
    if timestamp:
        parsed_timestamp = validate_datetime_with_tz(timestamp)

    # Get application context
    app = ctx.obj

    if not is_no_build and not build_name:
        raise typer.BadParameter("Error: Missing option '--build'")

    if is_no_build:
        build_name = NO_BUILD_BUILD_NAME

    # After validation, build_name is guaranteed to be non-None
    assert build_name is not None

    tracking_client = TrackingClient(Command.RECORD_SESSION, app=app)
    client = LaunchableClient(app=app, tracking_client=tracking_client)

    sub_path = f"builds/{build_name}/test_session_names/{session}"
    try:
        res = client.request("get", sub_path)

        if res.status_code != 404:
            msg = f"This session name ({session}) is already used. Please set another name."
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
        "testSuite": test_suite,
        "timestamp": parsed_timestamp.isoformat() if parsed_timestamp else None,
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
        sub_path = f"builds/{build_name}/test_sessions"
        res = client.request("post", sub_path, payload=payload)

        if res.status_code == HTTPStatus.NOT_FOUND:
            msg = f"Build {build_name} was not found." \
                f"Make sure to run `launchable record build --build {build_name}` before you run this command."
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
            assert build_name is not None

    except Exception as e:
        tracking_client.send_error_event(
            event_name=Tracking.ErrorEvent.INTERNAL_CLI_ERROR,
            stack_trace=str(e),
        )
        client.print_exception_and_recover(e)

    try:
        add_session_name(
            client=client,
            build_name=build_name,
            session_id=session_id,
            session_name=session,
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
    sub_path = f"builds/{build_name}/test_sessions/{session_id}"
    payload = {
        "name": session_name
    }
    res = client.request("patch", sub_path, payload=payload)

    if res.status_code == HTTPStatus.NOT_FOUND:
        typer.secho(
            f"Test session {session_id} was not found. Record session may have failed.",
            fg=typer.colors.YELLOW, err=True
        )
        sys.exit(1)
    if res.status_code == HTTPStatus.BAD_REQUEST:
        typer.secho(
            "You cannot use test session name {} since it is already used by other test session in your workspace. "
            "The record session is completed successfully without session name.",
            fg=typer.colors.YELLOW, err=True)
        sys.exit(1)

    res.raise_for_status()
