import click

from launchable.utils.click import GroupWithAlias

from .test_sessions import test_sessions


@click.group(cls=GroupWithAlias)
def stats():
    pass


stats.add_command(test_sessions)
