from .tests import tests
import click


@click.group()
def optimize():
    pass


optimize.add_command(tests)
