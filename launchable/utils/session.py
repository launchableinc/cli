import os
import sys
from pathlib import Path
from typing import Optional
import datetime
import json
from .logger import Logger

SESSION_DIR_KEY = 'LAUNCHABLE_SESSION_DIR'


def _session_file_dir() -> Path:
    return Path(os.environ.get(SESSION_DIR_KEY) or os.getcwd()).expanduser()


def _session_file_path() -> Path:
    return _session_file_dir() / ".launchable"


def read_session(build_name: str) -> Optional[str]:
    f = _session_file_path()
    try:
        if not f.exists():
            return None

        # TODO: check build name from file
        with open(f) as file:
            session_file = json.load(file)
            return session_file["session"]

    except Exception as e:
        raise Exception("Can't read {}".format(f)) from e


def write_build(build_name: str) -> None:
    try:
        if not _session_file_dir().exists():
            _session_file_dir().mkdir(parents=True, exist_ok=True)

        session_file = {}
        session_file["build"] = build_name

        with open(_session_file_path(), 'w') as f:
            json.dump(session_file, f)

    except Exception as e:
        raise Exception("Can't write to {}. Perhaps set the {} environment variable to specify an alternative writable path?".format(
            _session_file_path(), SESSION_DIR_KEY)) from e


def write_session(build_name: str, session_id: str) -> None:
    try:
        # TODO: file check when write session, file doesn't exit is invalid
        if not _session_file_dir().exists():
            _session_file_dir().mkdir(parents=True, exist_ok=True)

        session_file = {}
        session_file["build"] = build_name
        session_file["session"] = session_id

        with open(_session_file_path(), 'w') as f:
            json.dump(session_file, f)

    except Exception as e:
        raise Exception("Can't write to {}. Perhaps set the {} environment variable to specify an alternative writable path?".format(
            _session_file_path(), SESSION_DIR_KEY)) from e


def remove_session() -> None:
    """
    Call it after closing a session
    """
    if _session_file_path().exists():
        _session_file_path().unlink()


def clean_session_files(days_ago: int = 0) -> None:
    """
    Call it each build start
    """
    remove_session()


def parse_session(session: str):
    try:
        # session format:
        # builds/<build name>/test_sessions/<test session id>
        _, build_name, _, session_id = session.split("/")
    except Exception as e:
        raise Exception("Can't parse session: {}".format(session)) from e

    return build_name, session_id
