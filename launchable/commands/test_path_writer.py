import click
from typing import Optional, Callable, List
from ..testpath import TestPath
from os.path import join


class TestPathWriter(object):
    base_path = Optional[str]

    def __init__(self):
        self._formatter = TestPathWriter.default_formatter
        self._separator = "\n"

    @classmethod
    def default_formatter(cls, x: TestPath):
        """default formatter that's in line with to_test_path(str)"""
        file_name = x[0]['name']
        if cls.base_path:
            # default behavior consistent with default_path_builder's relative path handling
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

    def write_file(self, file: str, test_paths:  List[TestPath]):
        open(file, "w+", encoding="utf-8").write(
            self.separator.join(self.formatter(t) for t in test_paths))

    def print(self, test_paths: List[TestPath]):
        click.echo(self.separator.join(self.formatter(t)
                                       for t in test_paths))
