import click
from launchable.utils.click import GroupWithAlias
from .subset import subset
from .tests import tests


@click.group(cls=GroupWithAlias)
def inspect():
    pass


inspect.add_command(subset)
inspect.add_command(tests)
