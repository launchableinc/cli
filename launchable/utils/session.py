import os
import sys
from pathlib import Path
from typing import Optional
import datetime
import hashlib
from .logger import Logger

SESSION_DIR_KEY = 'LAUNCHABLE_SESSION_DIR'
DEFAULT_SESSION_DIR = '~/.config/launchable/sessions/'


def _session_file_dir() -> Path:
    return Path(os.environ.get(SESSION_DIR_KEY) or DEFAULT_SESSION_DIR).expanduser()


def _session_file_path(build_name: str) -> Path:
    return _session_file_dir() / (hashlib.sha1("{}:{}".format(build_name, _get_session_id()).encode()).hexdigest() + ".txt")


def _get_session_id() -> str:
    # CircleCI changes unix session id each steps, so set non change variable
    # https://circleci.com/docs/2.0/env-vars/#built-in-environment-variables
    if os.environ.get("CIRCLECI") is not None:
        id = os.environ.get("CIRCLE_WORKFLOW_ID")
        if id is not None:
             return id
        Logger().warning("CIRCLECI environment variable is set but not CIRCLE_WORKFLOW_ID")

    # Jenkins pipeline also launches every process as a new session, so better to scope this to a particular build.
    # For freestyle job types that do not do this, session IDs do not distinguish different builds, so that is a problem, too.
    #
    # See: https://github.com/jenkinsci/lib-durable-task/blob/6e020747205cb5aca5af757bc0d2a302c42bdb79/src/cmd/bash/durable_task_monitor.go#L41
    # See: https://www.jenkins.io/doc/book/pipeline/jenkinsfile/#using-environment-variables
    if os.environ.get("JENKINS_URL") is not None:
        id = os.environ.get("BUILD_URL")
        if id is not None:
            return id
        Logger().warning("JENKINS_URL environment variable is set but not BUILD_URL")

    if sys.platform == "win32":
        import wmi # type: ignore
        c = wmi.WMI()
        wql = "Associators of {{Win32_Process='{}'}} Where Resultclass = Win32_LogonSession Assocclass = Win32_SessionProcess".format(os.getpid())
        res = c.query(wql)
        return str(res[0].LogonId)
    else:
        return str(os.getsid(os.getpid()))


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

            if sys.platform == "win32":
                # Windows sometimes misses to delete session files at Unit Test
                microseconds = -10
            else:
                microseconds = 0

            clean_date = datetime.datetime.now() - datetime.timedelta(days=days_ago, microseconds=microseconds)
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
