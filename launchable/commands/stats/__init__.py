from .test_sessions import test_sessions
import click
from launchable.utils.click import GroupWithAlias


@click.group(cls=GroupWithAlias)
def stats():
    pass


stats.add_command(test_sessions)
