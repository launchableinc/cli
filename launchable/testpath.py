import os.path
import pathlib
import subprocess
import sys
from typing import Dict, List, Optional

# Path component is a node in a tree.
# It's the equivalent of a short file/directory name in a file system.
# In our abstraction, it's represented as arbitrary bag of attributes
TestPathComponent = Dict[str, str]

# TestPath is a full path to a node in a tree from the root
# It's the equivalent of an absolute file name in a file system
TestPath = List[TestPathComponent]


class FilePathNormalizer:
    """Normalize file paths based on the Git repository root

    Some test runners output absolute file paths. This is not preferrable when
    making statistical data on tests as the absolute paths can vary per machine
    or per run. FilePathNormalizer guesses the relative paths based on the Git
    repository root.
    """
    def __init__(self,
                 base_path: Optional[str] = None,
                 no_base_path_inference: bool = False):
        self._base_path = base_path
        self._no_base_path_inference = no_base_path_inference
        self._inferred_base_path = None  # type: Optional[str]

    def relativize(self, p: str) -> str:
        return str(self._relativize(pathlib.Path(os.path.normpath(p))))

    def _relativize(self, p: pathlib.Path) -> pathlib.Path:
        if not p.is_absolute():
            return p

        if self._base_path:
            return p.relative_to(self._base_path)

        if self._no_base_path_inference:
            return p

        if not self._inferred_base_path:
            self._inferred_base_path = self._auto_infer_base_path(p)

        if self._inferred_base_path:
            return p.relative_to(self._inferred_base_path)

        return p

    def _auto_infer_base_path(self, p: pathlib.Path) -> Optional[str]:
        p = p.parent
        while p != p.root and not p.exists():
            p = p.parent
        try:
            toplevel = subprocess.check_output(
                ['git', 'rev-parse', '--show-superproject-working-tree'],
                cwd=str(p),
                stderr=subprocess.DEVNULL,
                universal_newlines=True).strip()
            if toplevel:
                return toplevel
            return subprocess.check_output(
                ['git', 'rev-parse', '--show-toplevel'],
                cwd=str(p),
                stderr=subprocess.DEVNULL,
                universal_newlines=True).strip()
        except subprocess.CalledProcessError as e:
            # Cannot infer the Git repo. Continue with the abs path...
            return None
