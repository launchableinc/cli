from .test import test
import click


@click.group()
def optimize():
    pass


optimize.add_command(test)
