import click
import os
import json
from pathlib import Path
import shutil
from typing import Optional
import datetime
import hashlib

SESSION_DIR_KEY = 'LAUNCHABLE_SESSION_DIR'
DEFAULT_SESSION_DIR = '~/.config/launchable/sessions/'


def _session_file_dir() -> Path:
    return Path(os.environ.get(SESSION_DIR_KEY) or DEFAULT_SESSION_DIR).expanduser()


def _session_file_path(build_name: str) -> Path:
    return _session_file_dir() / (hashlib.sha1("{}:{}".format(build_name, os.getsid(os.getpid())).encode()).hexdigest() + ".txt")


def read_session(build_name: str) -> Optional[str]:
    f = _session_file_path(build_name)
    try:
        if not f.exists():
            return None
        return f.read_text()
    except Exception as e:
        raise Exception("Can't read {}".format(f)) from e


def write_session(build_name: str, session_id: str) -> None:
    try:
        if not _session_file_dir().exists():
            _session_file_dir().mkdir(parents=True, exist_ok=True)

        _session_file_path(build_name).write_text(session_id)
    except Exception as e:
        raise Exception("Can't write to {}. Perhaps set the {} environment variable to specify an alternative writable path?".format(
            _session_file_path(build_name), SESSION_DIR_KEY)) from e


def remove_session(build_name: str) -> None:
    """
    Call it after closing a session
    """
    if _session_file_path(build_name).exists():
        _session_file_path(build_name).unlink()


def clean_session_files(days_ago: int = 0) -> None:
    """
    Call it each build start
    """
    if _session_file_dir().exists():
        for child in _session_file_dir().iterdir():
            file_created = datetime.datetime.fromtimestamp(
                child.stat().st_mtime)
            clean_date = datetime.datetime.now() - datetime.timedelta(days=days_ago)
            if file_created < clean_date:
                child.unlink()
