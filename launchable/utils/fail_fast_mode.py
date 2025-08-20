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


def _exit_if_errors(errors: List[str]):
    if errors:
        msg = "\n".join(map(lambda x: click.style(x, fg='red'), errors))
        click.echo(msg, err=True)
        sys.exit(1)
