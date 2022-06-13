import click
from typing import Optional
from ..utils.session import read_build, read_session


def find_or_create_session(context: click.core.Context, session: Optional[str], build_name: Optional[str], is_evaluation: Optional[bool], flavor=[]) -> Optional[str]:
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
            "No saved build name found.\nTo fix this, run `launchable record build`.\nIf you already ran this command on a different machine, use the --session option. See https://docs.launchableinc.com/sending-data-to-launchable/managing-complex-test-session-layouts", fg="yellow"))

    else:
        if build_name and saved_build_name != build_name:
            raise click.UsageError(click.style(
                "The build name you provided ({}) is different from the last build name recorded on this machine ({}).\nMake sure to run `launchable record build --name {}` before you run this command.\nIf you already recorded this build on a different machine, use the --session option instead of --build. See https://docs.launchableinc.com/sending-data-to-launchable/managing-complex-test-session-layouts".format(build_name, saved_build_name, build_name), fg="yellow"))

        saved_session_id, saved_is_evaluation = read_session(saved_build_name)
        if saved_session_id:
            if saved_is_evaluation and saved_is_evaluation != is_evaluation:
                # TODO (taka): should provide the document link for debug.
                raise click.UsageError(
                    'save_is_evaluation and --evaluation does not match'.format(saved_is_evaluation, is_evaluation))
            return saved_session_id
        else:
            context.invoke(
                session_command, build_name=saved_build_name, save_session_file=True, is_evaluation=bool(is_evaluation), print_session=False, flavor=flavor)
            return read_session(saved_build_name)
