from .build import build
from .commit import commit
import click


@click.group()
def record():
    pass


record.add_command(build)
record.add_command(commit)
