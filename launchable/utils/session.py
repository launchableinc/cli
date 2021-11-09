import os
import sys
import json
from pathlib import Path
from typing import Optional
import datetime

SESSION_DIR_KEY = 'LAUNCHABLE_SESSION_DIR'
DEFAULT_SESSION_DIR = '~/.config/launchable/sessions/'


def _session_file_dir() -> Path:
    return Path(os.environ.get(SESSION_DIR_KEY) or os.getcwd()).expanduser()


def _session_file_path() -> Path:
    return _session_file_dir() / ".launchable"


def _parse_session_file():
    try:
        with open(_session_file_path()) as session_file:
            session = json.load(session_file)

        return session.get("build"), session.get("test_session", "")

    except Exception as e:
        raise Exception("Can't parse session file: {}".format(
            _parse_session_file())) from e


def write_build(build_name: str) -> None:
    try:
        if not _session_file_dir().exists():
            _session_file_dir().mkdir(parents=True, exist_ok=True)

        if (_session_file_path().exists()):
            exist_build_name = read_build()
            if build_name != exist_build_name:
                raise Exception(
                    "You're going to save another build name. Make sure <TODO>")

        session = {}
        session["build"] = build_name
        with open(_session_file_path(), 'w') as session_file:
            json.dump(session, session_file)

    except Exception as e:
        raise Exception("Can't write to {}. Perhaps set the {} environment variable to specify an alternative writable path?".format(
            _session_file_path(), SESSION_DIR_KEY)) from e


def read_build() -> str:
    try:
        with open(_session_file_path()) as session_file:
            session = json.load(session_file)
            return session.get("build")

    except Exception as e:
        raise Exception("Can't load build name from test session file.") from e


def read_session(build_name: str) -> Optional[str]:
    try:
        f = _session_file_path()
        if not f.exists():
            return None
        build, session_id = _parse_session_file()

        if build != build_name:
            raise Exception("TODO: set build name is different")

        return session_id
    except Exception as e:
        raise Exception("Can't read {}".format(f)) from e


def write_session(build_name: str, session_id: str) -> None:
    try:
        f = _session_file_path()
        if not f.exists():
            raise Exception(
                "TODO: session file doesn't exist. build name is needed to include")

        saved_build_name, saved_session_id = _parse_session_file()
        if saved_build_name == "":
            raise Exception("TODO: have to run recrod build before")

        if saved_build_name != "" and saved_build_name != build_name:
            raise Exception("TODO: build name is different")

        if saved_session_id != "" and saved_session_id != session_id:
            raise Exception(
                "TODO: test session id is different")

        session = {}
        session["build"] = build_name
        session["test_session"] = session_id
        with open(_session_file_path(), 'w') as session_file:
            json.dump(session, session_file)
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
