import click
import os
import json
from pathlib import Path
from typing import Optional

session_file_path = Path('~/.config/launchable/session.json').expanduser()


class SessionError(Exception):
    pass


def read_session(build_name: str) -> Optional[str]:
    if not session_file_path.exists():
        raise SessionError(
            "No session file. Please write session {}".format(session_file_path))

    with session_file_path.open('r') as json_file:
        try:
            data = json.load(json_file)
            return data.get("{}:{}".format(build_name, os.getsid(os.getpid())))
        except json.JSONDecodeError as e:
            raise SessionError(
                "Invalid session file. Please remove {}".format(session_file_path))


def write_session(build_name: str, session_id: str) -> None:
    if session_file_path.exists():
        with session_file_path.open('r') as json_file:
            try:
                data = json.load(json_file)
            except json.JSONDecodeError as e:
                raise SessionError(
                    "Invalid session file. Please remove {}".format(session_file_path))
    else:
        session_file_path.parent.mkdir(parents=True, exist_ok=True)
        session_file_path.touch()
        data = {}

    with session_file_path.open('w') as json_file:
        data["{}:{}".format(build_name, os.getsid(os.getpid()))] = session_id
        json.dump(data, json_file)


def remove_session(build_name: str) -> None:
    """
    Call it after closing a session
    """
    if not session_file_path.exists():
        raise SessionError(
            "No session file. Please write session {}".format(session_file_path))
    with session_file_path.open('r') as json_file:
        try:
            data = json.load(json_file)
        except json.JSONDecodeError as e:
            raise SessionError(
                "Invalid session file. Please remove {}".format(session_file_path))

    with session_file_path.open('w') as json_file:
        del data["{}:{}".format(build_name, os.getsid(os.getpid()))]
        json.dump(data, json_file)


def remove_session_file() -> None:
    """
    Call it each build start
    """
    if session_file_path.exists():
        session_file_path.unlink()
