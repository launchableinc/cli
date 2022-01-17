import click
from typing import Optional
from ..utils.session import read_build, read_session


def find_or_create_session(context: click.core.Context, session: Optional[str], build_name: Optional[str], flavor=[]) -> Optional[str]:
    """Determine the test session ID to be used.

    1. If the user explicitly provides the session id via the `--session` option
    2. If the user gives no options, the current session ID is read from the session file tied to $PWD,
       or one is created from the current build name. See https://github.com/launchableinc/cli/pull/342
    3. The `--build` option is legacy compatible behaviour, in which case a session gets created and tied
       to the build.

    Args:
        session: The --session option value
        build_name: The --build option value
    """
    from .record.session import session as session_command

    if session:
        return session

    saved_build_name = read_build()
    if not saved_build_name:
        raise click.UsageError(click.style(
            "Have you run `launchable record build`?\nIf not, please do. If it was run elsewhere/earlier, please use the --session option", fg="yellow"))

    else:
        if build_name and saved_build_name != build_name:
            raise click.UsageError(click.style(
                "Given build name ({}) is different from when you ran `launchable record build --name {}`.\nMake sure to run `launchable record build --name {}` before.".format(build_name, saved_build_name, build_name), fg="yellow"))

        session_id = read_session(saved_build_name)
        if session_id:
            return session_id
        else:
            context.invoke(
                session_command, build_name=saved_build_name, save_session_file=True, print_session=False, flavor=flavor)
            return read_session(saved_build_name)
