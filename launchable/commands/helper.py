import click
from typing import Optional
from ..utils.session import read_build, read_session


def _validate_session_and_build_name(session: Optional[str], build_name: Optional[str]):
    if session and build_name:
        raise click.UsageError(
            'Only one of --build or --session should be specified')

    if session is None and build_name is None:
        raise click.UsageError(
            'Either --build or --session has to be specified')


def find_or_create_session(context, session: Optional[str], build_name: Optional[str], flavor=[]) -> Optional[str]:
    _validate_session_and_build_name(session, build_name)
    from .record.session import session as session_command

    if session:
        return session
    else:
        if not build_name:
            raise click.UsageError(click.style(
                "Make sure to run `launchable record build --name {}` before, \nOr this command was ran on another machine what was ran `launchable recrod build` command. So please use --session option to run".format(build_name), fg="yellow"))

        session_id = read_session(build_name)
        if session_id:
            return session_id
        else:
            context.invoke(
                session_command, build_name=build_name, save_session_file=True, print_session=False, flavor=flavor)
            return read_session(build_name)
