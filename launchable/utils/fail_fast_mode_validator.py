import sys
from typing import List, Optional, Sequence, Tuple

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
        session: Optional[str] = None,
        links: Sequence[Tuple[str, str]] = (),
        is_observation: bool = False,
        flavor: Sequence[Tuple[str, str]] = (),
    ):
        self.command = command
        self.fail_fast_mode = fail_fast_mode
        self.build = build
        self.is_no_build = is_no_build
        self.test_suite = test_suite
        self.session = session
        self.links = links
        self.is_observation = is_observation
        self.flavor = flavor
        self.errors: List[str] = []

    def validate(self):
        if not self.fail_fast_mode:
            return

        if self.command == Command.RECORD_SESSION:
            self._validate_record_session()
        if self.command == Command.SUBSET:
            self._validate_subset()
        if self.command == Command.RECORD_TESTS:
            self._validate_record_tests()

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

        self._print_errors()

    def _validate_require_session_option(self, cmd_name: str):
        if self.is_no_build:
            self.errors.append("Your workspace doesn't support the `--no-build` option in the {} command.".format(cmd_name))
            self.errors.append(
                "Please run `launchable record build` command to create a build first, then run `launchable record session` command to create a session.\n")  # noqa: E501

        if self.build:
            self.errors.append("Your workspace doesn't support the `--build` option to execute the {} command.".format(cmd_name))
            self.errors.append("Please run `launchable record sessions` command to create a session first.\n")

        if self.session is None:
            self.errors.append(
                "Your workspace requires the use of `--session` option to execute the {} command.".format(cmd_name))
            self.errors.append("Please run `launchable record session` command to create a session first.\n")

        if self.test_suite:
            self.errors.append("Your workspace doesn't support the `--test-suite` option in the {} command. Please set the option to the `record session` command instead.".format(cmd_name))  # noqa: E501

        if self.is_observation:
            self.errors.append(
                "Your workspace doesn't support the `--observation` option in the {} command. Please set the option to the `record session` command instead.".format(cmd_name))  # noqa: E501

        if len(self.flavor) > 0:
            self.errors.append(
                "Your workspace doesn't support the `--flavor` option in the {} command. Please set the option to the `record session` command instead.".format(cmd_name))  # noqa: E501

        if len(self.links) > 0:
            self.errors.append(
                "Your workspace doesn't support the `--link` option in the {} command. Please set the option to the `record session` command instead.".format(cmd_name))  # noqa: E501

    def _validate_subset(self):
        self._validate_require_session_option("subset")
        self._print_errors()

    def _validate_record_tests(self):
        self._validate_require_session_option("record tests")
        self._print_errors()

    def _print_errors(self):
        if len(self.errors) > 0:
            msg = "\n".join(map(lambda x: click.style(x, fg='red'), self.errors))
            click.echo(msg, err=True)
            sys.exit(1)
