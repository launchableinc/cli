import click
from typing import Optional
from ..utils.session import read_build, read_session


def find_or_create_session(context, session: Optional[str], build_name: Optional[str], flavor=[]) -> Optional[str]:
    from .record.session import session as session_command

    saved_build_name = read_build()
    if build_name and saved_build_name != build_name:
        raise click.UsageError(click.style(
            "Build option value ({}) is different from when you ran `launchable record build --name {}`.\nMake sure to run `launchable record build --name {}` before.".format(build_name, saved_build_name, build_name), fg="yellow"))

    if session:
        return session
    else:
        if not saved_build_name:
            raise click.UsageError(click.style(
                "Make sure to run `launchable record build --name {}` before, \nOr this command was ran on another machine what was ran `launchable recrod build` command. So please use --session option to run".format(build_name), fg="yellow"))

        session_id = read_session(saved_build_name)
        if session_id:
            return session_id
        else:
            context.invoke(
                session_command, build_name=saved_build_name, save_session_file=True, print_session=False, flavor=flavor)
            return read_session(saved_build_name)
