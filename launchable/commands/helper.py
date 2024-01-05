from typing import List, Optional

import click

from launchable.utils.no_build import NO_BUILD_BUILD_NAME
from launchable.utils.tracking import TrackingClient

from ..utils.launchable_client import LaunchableClient
from ..utils.session import read_build, read_session


def require_session(
        session: Optional[str],
) -> Optional[str]:
    """Ascertain the contextual test session to operate a CLI command for. If one doesn't exit, fail.

    1. If the user explicitly provides the session id via the `--session` option
    2. If the user gives no options, the current session ID is read from the session file tied to $PWD.
       See https://github.com/launchableinc/cli/pull/342
    """
    if session:
        return session

    session = read_session(require_build())
    if session:
        return session

    raise click.UsageError(
        click.style(
            "No saved test session found.\n"
            "If you already created a test session on a different machine, use the --session option. "
            "See https://docs.launchableinc.com/sending-data-to-launchable/managing-complex-test-session-layouts",
            fg="yellow"))


def require_build() -> str:
    """
    Like read_build() but fail if a build doesn't exist
    """
    b = read_build()
    if not b:
        raise click.UsageError(
            click.style(
                "No saved build name found.\n"
                "To fix this, run `launchable record build`.\n"
                "If you already ran this command on a different machine, use the --session option. "
                "See https://www.launchableinc.com/docs/sending-data-to-launchable/using-the-launchable-cli/"
                "recording-test-results-with-the-launchable-cli/managing-complex-test-session-layouts/",
                fg="yellow"))
    return b


def find_or_create_session(
    context: click.core.Context,
    session: Optional[str],
    build_name: Optional[str],
    tracking_client: TrackingClient,
    flavor=[],
    is_observation: bool = False,
    links: List[str] = [],
    is_no_build: bool = False,
    lineage: Optional[str] = None,
) -> Optional[str]:
    """Determine the test session ID to be used.

    1. If the user explicitly provides the session id via the `--session` option
    2. If the user gives no options, the current session ID is read from the session file tied to $PWD,
       or one is created from the current build name. See https://github.com/launchableinc/cli/pull/342
    3. The `--build` option is legacy compatible behaviour, in which case a session gets created and tied
       to the build. This usage still requires a locally recorded build name that must match the specified name.
       Kohsuke is not sure what the historical motivation for this behaviour is.

    Args:
        session: The --session option value
        build_name: The --build option value
        flavor: The --flavor option values
        is_observation: The --observation value
        links: The --link option values
        is_no_build: The --no-build option value
        lineage: lineage option value
    """
    from .record.session import session as session_command

    if session:
        _check_observation_mode_status(session, is_observation, tracking_client=tracking_client)
        return session

    if is_no_build:
        context.invoke(
            session_command,
            build_name=NO_BUILD_BUILD_NAME,
            save_session_file=True,
            print_session=False,
            flavor=flavor,
            is_observation=is_observation,
            links=links,
            is_no_build=is_no_build,
            lineage=lineage,
        )
        saved_build_name = read_build()
        return read_session(str(saved_build_name))

    saved_build_name = require_build()

    if build_name and saved_build_name != build_name:
        raise click.UsageError(
            click.style(
                "The build name you provided ({}) is different from the last build name recorded on this machine ({}).\n"
                "Make sure to run `launchable record build --name {}` before you run this command.\n"
                "If you already recorded this build on a different machine, use the --session option instead of --build. "
                "See https://www.launchableinc.com/docs/sending-data-to-launchable/using-the-launchable-cli/"
                "recording-test-results-with-the-launchable-cli/managing-complex-test-session-layouts/".format(
                    build_name, saved_build_name, build_name), fg="yellow", ))

    session_id = read_session(saved_build_name)
    if session_id:
        _check_observation_mode_status(session_id, is_observation, tracking_client=tracking_client)
        return session_id

    context.invoke(
        session_command,
        build_name=saved_build_name,
        save_session_file=True,
        print_session=False,
        flavor=flavor,
        is_observation=is_observation,
        links=links,
        is_no_build=is_no_build,
        lineage=lineage,
    )
    return read_session(saved_build_name)


def _check_observation_mode_status(session: str, is_observation: bool, tracking_client: TrackingClient):
    if not is_observation:
        return

    client = LaunchableClient(tracking_client=tracking_client)
    res = client.request("get", session)

    # only check when the status code is 200 not to stop the command
    if res.status_code == 200:
        is_observation_in_recorded_session = res.json().get("isObservation", False)
        if is_observation and not is_observation_in_recorded_session:
            click.echo(
                click.style(
                    "WARNING: --observation flag was ignored. Observation mode can only be enabled for a test session "
                    "during its initial creation. "
                    "Add `--observation` option to the `launchable record session` command instead.",
                    fg='yellow'),
                err=True)
