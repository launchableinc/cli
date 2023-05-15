import hashlib
from datetime import tzinfo
from typing import Dict, List, Optional

from .git_log_parser import GitCommit
from .http_client import LaunchableClient


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode('utf8')).hexdigest()


def _format_tzinfo(tz: Optional[tzinfo]) -> int:
    if not tz:
        return 0
    delta = tz.utcoffset(None)
    if not delta:
        return 0
    return round(delta.total_seconds() / 60)


def _convert_git_commit(commit: GitCommit) -> Dict:
    changed_files = []
    for changed_file in commit.changed_files:
        cf = dict()
        cf['linesAdded'] = changed_file.added
        cf['linesDeleted'] = changed_file.deleted
        cf['status'] = 'MODIFY'
        cf['path'] = changed_file.path
        cf['pathTo'] = changed_file.path
        changed_files.append(cf)
    parents = dict()
    if len(commit.parents) > 0:
        # We don't know which diff is for which parent. Use the first parent.
        parents[commit.parents[0]] = changed_files
        for parent in commit.parents[1:len(commit.parents)]:
            parents[parent] = []

    d = dict()
    d['commitHash'] = commit.commit_hash
    d['authorEmailAddress'] = _sha256(commit.author_email)
    d['authorWhen'] = round(commit.author_time.timestamp() * 1000)
    d['authorTimezoneOffset'] = _format_tzinfo(commit.author_time.tzinfo)
    d['committerEmailAddress'] = _sha256(commit.committer_email)
    d['committerWhen'] = round(commit.committer_time.timestamp() * 1000)
    d['committerTimezoneOffset'] = _format_tzinfo(commit.committer_time.tzinfo)
    d['parentHashes'] = parents
    return d


def upload_commits(commits: List[GitCommit], dry_run: bool):
    payload = {
        'commits': [_convert_git_commit(commit) for commit in commits]
    }

    client = LaunchableClient(dry_run=dry_run)
    res = client.request("post", "commits/collect", payload=payload)
    res.raise_for_status()
