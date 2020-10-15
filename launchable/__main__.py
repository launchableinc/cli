from .version import __version__
import click
from .commands.record import record


@click.group()
@click.version_option(version=__version__, prog_name='launchable-cli')
def main():
    pass


main.add_command(record)

if __name__ == '__main__':
    main()
