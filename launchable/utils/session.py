import os
import sys
from pathlib import Path
from typing import Optional
import datetime

SESSION_DIR_KEY = 'LAUNCHABLE_SESSION_DIR'
DEFAULT_SESSION_DIR = '~/.config/launchable/sessions/'


def _session_file_dir() -> Path:
    return Path(os.environ.get(SESSION_DIR_KEY) or DEFAULT_SESSION_DIR).expanduser()


def _session_file_path() -> Path:
    return _session_file_dir() / ".launchable"


def _parse_session_file(text: str):
    try:
        build, session = text.split("#")
        _, build_name = build.split("=")
        _, session_id = session.split("=")

        return build_name, session_id
    except Exception as e:
        raise Exception("Can't parse session file: {}".format(text)) from e


def read_session(build_name: str) -> Optional[str]:
    f = _session_file_path()
    try:
        if not f.exists():
            return None
        build, session_id = _parse_session_file(f.read_text())

        if build != build_name:
            raise Exception("Build name is different between input:{} and saved:{}. Previous job might be failed.\nPlease confirm previous job result and run after removing {}".format(
                build_name, build, f))

        return session_id
    except Exception as e:
        raise Exception("Can't read {}".format(f)) from e


def write_session(build_name: str, session_id: str) -> None:
    try:
        if not _session_file_dir().exists():
            _session_file_dir().mkdir(parents=True, exist_ok=True)

        f = _session_file_path()
        if f.exists():
            saved_build_name, saved_session_id = _parse_session_file(
                f.read_text())
            if saved_build_name != "" and saved_build_name != build_name:
                raise Exception(
                    "Session file already exists but different bettween input:{} and saved:{}\nMake sture to confirm previous job result and run after removing {}".format(saved_build_name, build_name, f))

            if saved_session_id != session_id:
                raise Exception(
                    "Session file already exists but different session id bettween input:{} and saved:{}\nMake sture to confirm previous job result and run after removing {}".format(session_id, saved_session_id, f))

        f.write_text(
            "build={}#test_session={}".format(build_name, session_id))
    except Exception as e:
        raise Exception("Can't write to {}. Perhaps set the {} environment variable to specify an alternative writable path?".format(
            _session_file_path(), SESSION_DIR_KEY)) from e


def remove_session(build_name: str) -> None:
    """
    Call it after closing a session
    """
    if _session_file_path().exists():
        _session_file_path().unlink()


def clean_session_files(days_ago: int = 0) -> None:
    """
    Call it each build start
    """
    if _session_file_dir().exists():
        for child in _session_file_dir().iterdir():
            file_created = datetime.datetime.fromtimestamp(
                child.stat().st_mtime)

            if sys.platform == "win32":
                # Windows sometimes misses to delete session files at Unit Test
                microseconds = -10
            else:
                microseconds = 0

            clean_date = datetime.datetime.now() - datetime.timedelta(days=days_ago,
                                                                      microseconds=microseconds)
            if file_created < clean_date:
                child.unlink()


def parse_session(session: str):
    try:
        # session format:
        # builds/<build name>/test_sessions/<test session id>
        _, build_name, _, session_id = session.split("/")
    except Exception as e:
        raise Exception("Can't parse session: {}".format(session)) from e

    return build_name, session_id
