import json
from collections import namedtuple
from typing import Any, Dict, List, TextIO

import dateutil.parser

ChangedFile = namedtuple('ChangedFile', ['path', 'added', 'deleted'])

GitCommit = namedtuple('GitCommit', [
    'commit_hash', 'parents', 'author_email', 'author_time', 'committer_email',
    'committer_time', 'changed_files'
])


def parse_git_log(fp: TextIO) -> List[GitCommit]:
    """Parses the output of a git log command.

    This parses the output of `git log --pretty='format:{"commit": "%H",
    "parents": "%P", "authorEmail": "%ae", "authorTime": "%aI",
    "committerEmail": "%ce", "committerTime": "%cI"}' --numstat`
    """
    ret = []
    meta = {}  # type: Dict[str, Any]
    files = []  # type: List[ChangedFile]
    for idx, line in enumerate(fp):
        line = line.strip()
        if line == '':
            continue
        try:
            if line.startswith('{'):
                if len(meta) != 0:
                    ret.append(GitCommit(changed_files=files, **meta))
                    meta = {}
                    files = []
                d = json.loads(line)
                meta['commit_hash'] = d['commit']
                meta['parents'] = d['parents'].split(' ')
                meta['author_email'] = d['authorEmail']
                meta['author_time'] = dateutil.parser.parse(d['authorTime'])
                meta['committer_email'] = d['committerEmail']
                meta['committer_time'] = dateutil.parser.parse(
                    d['committerTime'])
            elif line.startswith('-'):
                # Ignore binary file changes
                pass
            else:
                added, deleted, path = line.split('\t', 3)
                files.append(ChangedFile(path=path, added=int(added), deleted=int(deleted)))
        except Exception as e:
            raise ValueError("Failed to parse the file at line {}: {}".format(idx + 1, e))
    if len(meta) != 0:
        ret.append(GitCommit(changed_files=files, **meta))
    return ret
