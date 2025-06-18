import sys
from typing import List, Optional

import click

from .commands import Command


class FailFastModeValidator:
    def __init__(
        self,
        command: Command = None,
        fail_fast_mode: bool = False,
        build: Optional[str] = None,
        is_no_build: bool = False,
        test_suite: Optional[str] = None,
    ):
        self.command = command
        self.fail_fast_mode = fail_fast_mode
        self.build = build
        self.is_no_build = is_no_build
        self.test_suite = test_suite
        self.errors: List[str] = []

        # Validate the record session command options
        self._validate_record_session()

    def validate(self):
        if not self.fail_fast_mode:
            return

        if self.command == Command.RECORD_SESSION:
            self._validate_record_session()

    def _validate_record_session(self):
        """
        Validate the record session command options
        """
        if self.build is None:
            self.errors.append("Your workspace requires the use of the `--build` option to issue a session.")
            if self.is_no_build:
                self.errors.append(
                    "If you want to import historical data, running `record build` command with the `--timestamp` option.")

        if self.test_suite is None:
            self.errors.append(
                "Your workspace requires the use of the `--test-suite` option to issue a session. Please specify a test suite such as \"unit-test\" or \"e2e\".")  # noqa: E501

        if self.command != "record_session":
            return

        if len(self.errors) > 0:
            msg = "\n".join(map(lambda x: click.style(x, fg='red'), self.errors))
            click.echo(msg, err=True)
            sys.exit(1)
