import glob
import os
import sys
from os.path import join, relpath, normpath
from typing import Callable, Union, Optional, List

import click

from .testpath import TestPath
from .utils.env_keys import REPORT_ERROR_KEY
from .utils.http_client import LaunchableClient
from .commands.helper import find_or_create_session


class Optimize:
    # test_paths: List[TestPath]  # doesn't work with Python 3.5

    # Where we take TestPath, we also accept a path name as a string.
    TestPathLike = Union[str, TestPath]

    def __init__(self, context :click.Context, base_path):
        """
            :param context
                    Click context that provides access to global options
                    TODO: rename to something more click specific
        """
        self.test_paths = []
        self.context = context
        self.base_path = base_path
        self._formatter = self.default_formatter
        self._separator = "\n"

    def default_formatter(self, x: TestPath):
        """default formatter that's in line with to_test_path(str)"""
        file_name = x[0]['name']
        if self.base_path:
            # default behavior consistent with default_path_builder's relative path handling
            file_name = join(str(self.base_path), file_name)
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

    def test_path(self, path: TestPathLike):
        def rel_base_path(path):
            if isinstance(path, str) and self.base_path:
                return normpath(relpath(path, start=self.base_path))
            else:
                return path

        if isinstance(path, str) and any(s in path for s in ('*', "?")):
            for i in glob.iglob(path, recursive=True):
                if os.path.isfile(i):
                    self.test_paths.append(
                        self.to_test_path(rel_base_path(i)))
            return

        """register one test"""
        self.test_paths.append(self.to_test_path(rel_base_path(path)))

    def stdin(self):
        """
        Returns sys.stdin, but after ensuring that it's connected to something reasonable.

        This prevents a typical problem where users think CLI is hanging because
        they didn't feed anything from stdin
        """
        if sys.stdin.isatty():
            click.echo(click.style(
                "Warning: this command reads from stdin but it doesn't appear to be connected to anything. Did you forget to pipe from another command?",
                fg='yellow'), err=True)
        return sys.stdin

    @staticmethod
    def to_test_path(x: TestPathLike) -> TestPath:
        """Convert input to a TestPath"""
        if isinstance(x, str):
            # default representation for a file
            return [{'type': 'file', 'name': x}]
        else:
            return x

    def scan(self, base: str, pattern: str,
             path_builder: Optional[Callable[[str], Union[TestPath, str, None]]] = None):
        """
        Starting at the 'base' path, recursively add everything that matches the given GLOB pattern

        scan('src/test/java', '**/*.java')

        'path_builder' is a function used to map file name into a custom test path.
        It takes a single string argument that represents the portion matched to the glob pattern,
        and its return value controls what happens to that file:
            - skip a file by returning a False-like object
            - if a str is returned, that's interpreted as a path name and
              converted to the default test path representation. Typically, `os.path.join(base,file_name)
            - if a TestPath is returned, that's added as is
        """

        if path_builder == None:
            # default implementation of path_builder creates a file name relative to `source` so as not
            # to be affected by the path
            def default_path_builder(file_name):
                file_name = join(base, file_name)
                if self.base_path:
                    # relativize against `base_path` to make the path name portable
                    file_name = normpath(
                        relpath(file_name, start=self.base_path))
                return file_name

            path_builder = default_path_builder

        for b in glob.iglob(base):
            for t in glob.iglob(join(b, pattern), recursive=True):
                if path_builder:
                    path = path_builder(os.path.relpath(t, b))
                if path:
                    self.test_paths.append(self.to_test_path(path))


