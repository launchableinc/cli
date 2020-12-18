from .build import build
from .commit import commit
from .tests import tests
from .session import session
import click


@click.group()
def record():
    pass


record.add_command(build)
record.add_command(commit)
record.add_command(tests)
record.add_command(session)
