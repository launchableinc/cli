import os.path
import pathlib
import subprocess
import sys
import urllib
from typing import Dict, List, Optional, Tuple

# Path component is a node in a tree.
# It's the equivalent of a short file/directory name in a file system.
# In our abstraction, it's represented as arbitrary bag of attributes
TestPathComponent = Dict[str, str]

# TestPath is a full path to a node in a tree from the root
# It's the equivalent of an absolute file name in a file system
TestPath = List[TestPathComponent]


def parse_test_path(tp_str: str) -> TestPath:
    """Parse a string representation of TestPath."""
    if tp_str == '':
        return []
    ret = []  # type: TestPath
    for component_str in tp_str.split('#'):
        if component_str == '&':
            # Technically, this should be mapped to {None:None}. But because the
            # TestPath definition is now Dict[str, str], not Dict[Optional[str],
            # Optinal[str]], we cannot add it. Fixing this definition needs to
            # fix callers not to assume they are always str. In practice, this
            # is a rare case. Do not appent {None: None} now...
            # ret.append({None: None})
            continue
        first = True
        component = {}
        for kv in component_str.split('&'):
            if first:
                first = False
                if kv:
                    (component['type'], component['name']) = _parse_kv(kv)
            else:
                (k, v) = _parse_kv(kv)
                component[k] = v
        ret.append(component)
    return ret


def _parse_kv(kv: str) -> Tuple[str, str]:
    kvs = kv.split('=')
    if len(kvs) != 2:
        raise ValueError('Malformed TestPath component: ' + kv)
    return (_decode_str(kvs[0]), _decode_str(kvs[1]))


def unparse_test_path(tp: TestPath) -> str:
    """Create a string representation of TestPath."""
    ret = []
    for component in tp:
        s = ''
        pairs = []
        if component.get('type', None) and component.get('name', None):
            s += _encode_str(component['type']) + \
                '=' + _encode_str(component['name'])
            for k, v in component.items():
                if k not in ('type', 'name'):
                    pairs.append((k, v))
        else:
            for k, v in component.items():
                if not k or not v:
                    continue
                pairs.append((k, v))
            if len(pairs) == 0:
                s = '&'
        pairs = sorted(pairs, key=lambda p: p[0])
        for (k, v) in pairs:
            s += '&'
            s += _encode_str(k) + '=' + _encode_str(v)
        ret.append(s)
    return '#'.join(ret)


def _decode_str(s: str) -> str:
    return urllib.parse.unquote(s)


def _encode_str(s: str) -> str:
    return s.replace('%', '%25').replace('=', '%3D').replace('#', '%23').replace('&', '%26')


def _relative_to(p: pathlib.Path, base: str) -> pathlib.Path:
    if sys.version_info[0:2] >= (3, 6):
        return p.resolve(strict=False).relative_to(base)
    else:
        try:
            resolved = p.resolve()
        except:
            resolved = p
        return resolved.relative_to(base)


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
            return _relative_to(p, self._base_path)

        if self._no_base_path_inference:
            return p

        if not self._inferred_base_path:
            self._inferred_base_path = self._auto_infer_base_path(p)

        if self._inferred_base_path:
            return _relative_to(p, self._inferred_base_path)

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
