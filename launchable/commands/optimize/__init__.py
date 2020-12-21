from .tests import tests
import click
from launchable.utils.click import GroupWithAlias


@click.group(cls=GroupWithAlias)
def optimize():
    pass


optimize.add_command(tests)
optimize.add_alias('test',tests)    # for backward compatibility
