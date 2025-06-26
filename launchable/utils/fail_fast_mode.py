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


def warning_and_exit_if_fail_fast_mode(message: str):
    color = 'yellow' if is_fail_fast_mode() else 'red'
    message = click.style(message, fg=color)

    click.echo(message, err=True)
    if is_fail_fast_mode():
        sys.exit(1)


class FailFastContext:
    command: Command
    build: Optional[str] = None
    is_no_build: bool = False
    test_suite: Optional[str] = None
    session: Optional[str] = None
    links: Sequence[Tuple[str, str]] = ()
    is_observation: bool = False
    flavor: Sequence[Tuple[str, str]] = ()


def fail_fast_validate(ctx: FailFastContext, fail_fast: bool = False):
    if not is_fail_fast_mode():
        return

    errors = []

    # Now, there isn't any validation for the `record session` command in fail-fast mode.
    if ctx.command in {Command.RECORD_TESTS, Command.SUBSET} and ctx.session:
        cmd_name = ctx.command.human_readable()
        if ctx.test_suite:
            errors.append(f"`--test-suite` is ignored in {cmd_name}. Add it to `record session` instead.")
        if ctx.is_observation:
            errors.append(f"`--observation` is ignored in {cmd_name}. Add it to `record session` instead.")
        if ctx.flavor:
            errors.append(f"`--flavor` is ignored in {cmd_name}. Add it to `record session` instead.")
        if ctx.links:
            errors.append(f"`--link` is ignored in {cmd_name}. Add it to `record session` instead.")

    _exit_if_errors(errors)


def _exit_if_errors(errors: List[str]):
    if len(errors) > 0:
        msg = "\n".join(map(lambda x: click.style(x, fg='red'), errors))
        click.echo(msg, err=True)
        sys.exit(1)
