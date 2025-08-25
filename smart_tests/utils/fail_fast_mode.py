import sys
from typing import List, Optional, Sequence, Tuple

import click

from .commands import Command

_fail_fast_mode_cache: Optional[bool] = None


def set_fail_fast_mode(enabled: bool):
    global _fail_fast_mode_cache
    _fail_fast_mode_cache = enabled


def is_fail_fast_mode() -> bool:
    if _fail_fast_mode_cache:
        return _fail_fast_mode_cache

    # Default to False if not set
    return False


def warn_and_exit_if_fail_fast_mode(message: str):
    color = 'red' if is_fail_fast_mode() else 'yellow'
    message = click.style(message, fg=color)

    click.echo(message, err=True)
    if is_fail_fast_mode():
        sys.exit(1)


class FailFastModeValidateParams:
    def __init__(self, command: Command, build: Optional[str] = None, is_no_build: bool = False,
                 test_suite: Optional[str] = None, session: Optional[str] = None,
                 links: Sequence[Tuple[str, str]] = (), is_observation: bool = False,
                 flavor: Sequence[Tuple[str, str]] = ()):
        self.command = command
        self.build = build
        self.is_no_build = is_no_build
        self.test_suite = test_suite
        self.session = session
        self.links = links
        self.is_observation = is_observation
        self.flavor = flavor


def fail_fast_mode_validate(params: FailFastModeValidateParams):
    if not is_fail_fast_mode():
        return

    if params.command == Command.RECORD_SESSION:
        _validate_record_session(params)
    if params.command == Command.SUBSET:
        _validate_subset(params)
    if params.command == Command.RECORD_TESTS:
        _validate_record_tests(params)


def _validate_require_session_option(params: FailFastModeValidateParams) -> List[str]:
    errors: List[str] = []
    cmd_name = params.command.display_name()
    if params.session:
        if params.test_suite:
            errors.append("`--test-suite` option was ignored in the {} command. Add `--test-suite` option to the `record session` command instead.".format(cmd_name))  # noqa: E501

        if params.is_observation:
            errors.append(
                "`--observation` was ignored in the {} command. Add `--observation` option to the `record session` command instead.".format(cmd_name))  # noqa: E501

        if len(params.flavor) > 0:
            errors.append(
                "`--flavor` option was ignored in the {} command. Add `--flavor` option to the `record session` command instead.".format(cmd_name))  # noqa: E501

        if len(params.links) > 0:
            errors.append(
                "`--link` option was ignored in the {} command. Add `link` option to the `record session` command instead.".format(cmd_name))  # noqa: E501

    return errors


def _validate_record_session(params: FailFastModeValidateParams):
    # Now, there isn't any validation for the `record session` command in fail-fast mode.
    return


def _validate_subset(params: FailFastModeValidateParams):
    errors = _validate_require_session_option(params)
    _exit_if_errors(errors)


def _validate_record_tests(params: FailFastModeValidateParams):
    errors = _validate_require_session_option(params)
    _exit_if_errors(errors)


def _exit_if_errors(errors: List[str]):
    if errors:
        msg = "\n".join(map(lambda x: click.style(x, fg='red'), errors))
        click.echo(msg, err=True)
        sys.exit(1)
