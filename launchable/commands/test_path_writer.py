import click
from typing import Optional, Callable, List
from ..testpath import TestPath
from os.path import join


class TestPathWriter():
    base_path = None

    def __init__(self, formatter: Callable[[TestPath], str] = None, separator: str = "\n"):
        self._formatter = formatter
        self.separator = separator

    def default_formatter(self, x: TestPath):
        """default formatter that's in line with to_test_path(str)"""
        file_name = x[0]['name']
        if base_path:
            # default behavior consistent with default_path_builder's relative path handling
            file_name = join(str(base_path), file_name)
        return file_name

    @property
    def formatter(self):
        if self._formatter:
            return self._formatter

        return self.default_formatter

    def write_file(self, file: str, test_paths:  List[TestPath]):
        open(file, "w+", encoding="utf-8").write(
            self.separator.join(self.formatter(t) for t in test_paths))

    def print(self, test_paths: List[TestPath]):
        click.echo(self.separator.join(self.formatter(t)
                                       for t in test_paths))
