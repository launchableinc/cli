from .session import session
import click
from launchable.utils.click import GroupWithAlias


@click.group(cls=GroupWithAlias)
def close():
    pass


close.add_command(session)
