"""Path name matching with extended GLOBs.

Primarily developed to interface with Maven, which supports "**", "*", and "?" as the special characters
"""
import re
from typing import Pattern


def is_path_separator(c: str):
    return c == '/' or c == '\\'


def compile(glob: str) -> Pattern:
    """Compiles a glob pattern like foo/**/*.txt into a """
    # fnmatch.fnmatch is close but it doesn't deal with paths well, including
    # '**'

    p = ""
    i = 0
    n = len(glob)
    while i < n:
        c = glob[i]
        i += 1

        if c == '*':
            if i < n and glob[i] == '*':
                i += 1
                if i < n and is_path_separator(glob[i]):
                    # '**/' matches any sub-directories or none
                    i += 1
                    p += "(.+[\\/])?"
                else:
                    # '**' used like **Test.java. Is this even legal?
                    p += ".*"
            else:
                p += "[^\\/]*"
        elif c == '?':
            p += "[^\\/]"
        elif is_path_separator(c):
            p += "[\\/]"
        else:
            p += re.escape(c)

    return re.compile(p)
