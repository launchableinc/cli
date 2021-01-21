import click
import os
import json
from pathlib import Path
import shutil
from typing import Optional

session_file_dir_path = Path('~/.config/launchable/sessions/').expanduser()


def _session_file_path(build_name: str) -> Path:
    return session_file_dir_path / "{}:{}.txt".format(build_name, os.getsid(os.getpid()))


def read_session(build_name: str) -> Optional[str]:    
    if not _session_file_path(build_name).exists():
        return None

    with _session_file_path(build_name).open('r') as session_file:
        return session_file.read()
        

def write_session(build_name: str, session_id: str) -> None:
    if not session_file_dir_path.exists():
        session_file_dir_path.mkdir(parents=True, exist_ok=True)

    with _session_file_path(build_name).open('w+') as session_file:
        session_file.write(session_id)


def remove_session(build_name: str) -> None:
    """
    Call it after closing a session
    """
    if not _session_file_path(build_name).exists():
        raise SessionError(
            "No session file. Please write session {}".format(_session_file_path(build_name)))

    if _session_file_path(build_name).exists():
        _session_file_path(build_name).unlink()


def remove_session_files() -> None:
    """
    Call it each build start
    """
    if session_file_dir_path.exists():
        shutil.rmtree(session_file_dir_path)
