import click

from launchable.utils.click import GroupWithAlias

from .subsets import subsets


@click.group(cls=GroupWithAlias)
def compare():
    pass


compare.add_command(subsets)
