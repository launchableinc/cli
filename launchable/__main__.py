from .version import __version__
import click
import importlib
import logging
from os.path import dirname, basename, join
from glob import glob
from .commands.record import record
from .commands.subset import subset
from .commands.verify import verify
from .utils import logger


@click.group()
@click.version_option(version=__version__, prog_name='launchable-cli')
@click.option(
    '--log-level',
    'log_level',
    help='Set logger\'s log level (CRITICAL, ERROR, WARNING, AUDIT, INFO, DEBUG).',
    type=str,
    default=logger.LOG_LEVEL_DEFAULT_STR,
)
def main(log_level):
    level = logger.get_log_level(log_level)
    logging.basicConfig(level=level)

    # load all test runners
    for f in glob(join(dirname(__file__), 'test_runners', "*.py")):
        f = basename(f)[:-3]
        if f == '__init__':
            continue
        importlib.import_module('launchable.test_runners.%s' % f)


main.add_command(record)
main.add_command(subset)
main.add_command(verify)


if __name__ == '__main__':
    main()
