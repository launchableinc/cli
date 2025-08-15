from typing import Tuple

import typer

from smart_tests.utils.no_build import NO_BUILD_BUILD_NAME
from smart_tests.utils.tracking import TrackingClient

from ..app import Application
from ..utils.launchable_client import LaunchableClient


def get_session_id(session: str, build_name: str | None, is_no_build: bool, client: LaunchableClient) -> str:
    """Get session ID using session name and build configuration.

    Args:
        session: Session name
        build_name: Build name (required when is_no_build is False)
        is_no_build: Whether --no-build flag is set
        client: LaunchableClient instance

    Returns:
        Session ID string
    """
    # Determine build_name based on --no-build flag
    if is_no_build:
        effective_build_name = NO_BUILD_BUILD_NAME
    else:
        if not build_name:
            raise typer.BadParameter(
                '--build option is required when --no-build is not specified')
        effective_build_name = build_name

    # Get session ID using session name
    sub_path = f"builds/{effective_build_name}/test_session_names/{session}"
    res = client.request("get", sub_path)
    res.raise_for_status()

    return f"builds/{effective_build_name}/test_sessions/{res.json().get('id')}"


def validate_session_format(session: str):
    """Validate session format to ensure it follows the expected pattern.

    Args:
        session: Session string to validate

    Raises:
        ValueError: If session format is invalid
    """
    # session format: builds/<build name>/test_sessions/<test session id>
    if session.count("/") != 3:
        raise ValueError(
            f"Invalid session format: {session}. Expected format: builds/{{build_name}}/test_sessions/{{test_session_id}}")


def parse_session(session_id: str) -> Tuple[str, str]:
    """Parse session ID to extract build name and test session ID.

    Args:
        session_id: Session ID in format "builds/{build_name}/test_sessions/{test_session_id}"

    Returns:
        Tuple of (build_name, test_session_id)

    Raises:
        ValueError: If session_id format is invalid
    """
    validate_session_format(session_id)
    import re
    match = re.match(r"builds/([^/]+)/test_sessions/(.+)", session_id)
    if match:
        return match.group(1), match.group(2)
    else:
        raise ValueError(
            f"Invalid session ID format: {session_id}. Expected format: builds/{{build_name}}/test_sessions/{{test_session_id}}")


def _check_observation_mode_status(session: str, is_observation: bool,
                                   tracking_client: TrackingClient, app: Application | None = None):
    if not is_observation:
        return

    client = LaunchableClient(tracking_client=tracking_client, app=app)
    res = client.request("get", session)

    # only check when the status code is 200 not to stop the command
    if res.status_code == 200:
        is_observation_in_recorded_session = res.json().get("isObservation", False)
        if is_observation and not is_observation_in_recorded_session:
            typer.secho(
                "WARNING: --observation flag was ignored. Observation mode can only be enabled for a test session "
                "during its initial creation. "
                "Add `--observation` option to the `smart-tests record session` command instead.",
                fg=typer.colors.YELLOW,
                err=True)
