from .build import build
from .commit import commit
from .test import test
import click


@click.group()
def record():
    pass


record.add_command(build)
record.add_command(commit)
record.add_command(test)
