from typing import List, Optional

import click

from launchable.utils.no_build import NO_BUILD_BUILD_NAME

from ..utils.http_client import LaunchableClient
from ..utils.session import read_build, read_session


def find_or_create_session(
    context: click.core.Context,
    session: Optional[str],
    build_name: Optional[str],
    flavor=[],
    is_observation: bool = False,
    links: List[str] = [],
    is_no_build: bool = False,
) -> Optional[str]:
    """Determine the test session ID to be used.

    1. If the user explicitly provides the session id via the `--session` option
    2. If the user gives no options, the current session ID is read from the session file tied to $PWD,
       or one is created from the current build name. See https://github.com/launchableinc/cli/pull/342
    3. The `--build` option is legacy compatible behaviour, in which case a session gets created and tied
       to the build.

    Args:
        session: The --session option value
        build_name: The --build option value
    """
    from .record.session import session as session_command

    if session:
        _check_observation_mode_status(session, is_observation)
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
        )
        saved_build_name = read_build()
        return read_session(str(saved_build_name))

    saved_build_name = read_build()
    if not saved_build_name:
        raise click.UsageError(
            click.style(
                "No saved build name found.\n"
                "To fix this, run `launchable record build`.\n"
                "If you already ran this command on a different machine, use the --session option. "
                "See https://docs.launchableinc.com/sending-data-to-launchable/managing-complex-test-session-layouts",
                fg="yellow"))

    else:
        if build_name and saved_build_name != build_name:
            raise click.UsageError(
                click.style(
                    "The build name you provided ({}) is different from the last build name recorded on this machine ({}).\n"
                    "Make sure to run `launchable record build --name {}` before you run this command.\n"
                    "If you already recorded this build on a different machine, use the --session option instead of --build. "
                    "See https://docs.launchableinc.com/sending-data-to-launchable/managing-complex-test-session-layouts".format(
                        build_name, saved_build_name, build_name), fg="yellow", ))

        session_id = read_session(saved_build_name)
        if session_id:
            _check_observation_mode_status(session_id, is_observation)
            return session_id
        else:
            context.invoke(
                session_command,
                build_name=saved_build_name,
                save_session_file=True,
                print_session=False,
                flavor=flavor,
                is_observation=is_observation,
                links=links,
                is_no_build=is_no_build,
            )
            return read_session(saved_build_name)


def _check_observation_mode_status(session: str, is_observation: bool):
    if not is_observation:
        return

    client = LaunchableClient()
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
