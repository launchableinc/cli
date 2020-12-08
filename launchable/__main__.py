from .version import __version__
import click
from .commands.record import record
from .commands.optimize import optimize
from .commands.verify import verify


@click.group()
@click.version_option(version=__version__, prog_name='launchable-cli')
def main():
    pass


main.add_command(record)
main.add_command(optimize)
main.add_command(verify)

if __name__ == '__main__':
    main()
