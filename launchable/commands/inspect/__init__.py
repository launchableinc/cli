import click
from launchable.utils.click import GroupWithAlias
from .subset import subset


@click.group(cls=GroupWithAlias)
def inspect():
    pass


inspect.add_command(subset)
