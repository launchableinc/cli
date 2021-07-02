import click
from typing import Optional, Callable
from .record.session import session as session_command
from ..utils.session import read_session
from ..testpath import TestPath
from os.path import join


def _validate_session_and_build_name(session: Optional[str], build_name: Optional[str]):
    if session and build_name:
        raise click.UsageError(
            'Only one of --build or --session should be specified')

    if session is None and build_name is None:
        raise click.UsageError(
            'Either --build or --session has to be specified')


def find_or_create_session(context, session: Optional[str], build_name: Optional[str], flavor=[]) -> Optional[str]:
    _validate_session_and_build_name(session, build_name)

    if session:
        return session
    elif build_name:
        session_id = read_session(build_name)
        if session_id:
            return session_id
        else:
            context.invoke(
                session_command, build_name=build_name, save_session_file=True, print_session=False, flavor=flavor)
            return read_session(build_name)
    else:
        return None


class TestPathWriter(object):
    base_path = None

    def __init__(self):
        self._formatter = TestPathWriter.default_formatter
        self._separator = "\n"

    @classmethod
    def default_formatter(cls, x: TestPath):
        """default formatter that's in line with to_test_path(str)"""
        file_name = x[0]['name']
        if cls.base_path:
            # default behavior consistent with default_path_builder's relative path handling
            file_name = join(cls.base_path, file_name)
        return file_name

    @property
    def formatter(self) -> Callable[[TestPath], str]:
        """
        This function, if supplied, is used to format test names
        from the format Launchable uses to the format test runners expect.
        """
        return self._formatter

    @formatter.setter
    def formatter(self, v: Callable[[TestPath], str]):
        self._formatter = v

    @property
    def separator(self) -> str:
        return self._separator

    @separator.setter
    def separator(self, s: str):
        self._separator = s

    def write_file(self, file: str, test_paths: []):
        open(file, "w+", encoding="utf-8").write(
            self.separator.join(self.formatter(x=t) for t in test_paths))

    def print(self, test_paths: []):
        click.echo(self.separator.join(self.formatter(x=t)
                                       for t in test_paths))
