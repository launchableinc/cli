from .build import build
from .commit import commit
from .tests import tests
from .session import session
import click
from launchable.utils.click import GroupWithAlias


@click.group(cls=GroupWithAlias)
def record():
    pass


record.add_command(build)
record.add_command(commit)
record.add_command(tests)
# for backward compatibility
record.add_alias('test', tests)  # type: ignore
record.add_command(session)
