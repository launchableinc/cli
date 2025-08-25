from os.path import join
from typing import Callable, Dict, List

import typer

from ..app import Application
from ..testpath import TestPath


class TestPathWriter(object):
    base_path: str | None = None
    base_path_explicitly_set: bool = False  # Track if base_path was explicitly provided

    def __init__(self, app: Application):
        self._formatter: Callable[[TestPath], str] = TestPathWriter.default_formatter
        self._separator = "\n"
        self._same_bin_formatter: Callable[[str], Dict[str, str]] | None = None
        self.app = app

    @classmethod
    def default_formatter(cls, x: TestPath):
        """default formatter that's in line with to_test_path(str)"""
        file_name = x[0]['name']
        # Only prepend base_path if it was explicitly set via --base option
        # Auto-inferred base paths should not affect output formatting
        if cls.base_path and cls.base_path_explicitly_set:
            # default behavior consistent with default_path_builder's relative
            # path handling
            file_name = join(str(cls.base_path), file_name)
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

    def write_file(self, file: str, test_paths: List[TestPath]):
        open(file, "w+", encoding="utf-8").write(
            self.separator.join(self.formatter(t) for t in test_paths))

    def print(self, test_paths: List[TestPath]):
        typer.echo(self.separator.join(self.formatter(t)
                                       for t in test_paths))

    @property
    def same_bin_formatter(self) -> Callable[[str], Dict[str, str]] | None:
        return self._same_bin_formatter

    @same_bin_formatter.setter
    def same_bin_formatter(self, v: Callable[[str], Dict[str, str]]):
        self._same_bin_formatter = v
