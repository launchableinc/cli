from .version import __version__
import click
import importlib
import importlib.util
import logging
from os.path import dirname, basename, join
from glob import glob
from .commands.record import record
from .commands.subset import subset
from .commands.split_subset import split_subset
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
@click.option(
    '--plugins',
    'plugin_dir',
    help='Directory to load plugins from',
    type=click.Path(exists=True, file_okay=False)
)
def main(log_level, plugin_dir):
    level = logger.get_log_level(log_level)
    logging.basicConfig(level=level)

    # load all test runners
    for f in glob(join(dirname(__file__), 'test_runners', "*.py")):
        f = basename(f)[:-3]
        if f == '__init__':
            continue
        importlib.import_module('launchable.test_runners.%s' % f)

    # load all plugins
    if plugin_dir:
        for f in glob(join(plugin_dir, '*.py')):
            spec = importlib.util.spec_from_file_location(
                "launchable.plugins.{}".format(basename(f)[:-3]), f)
            plugin = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin)


main.add_command(record)
main.add_command(subset)
main.add_command(split_subset)
main.add_command(verify)


if __name__ == '__main__':
    main()
