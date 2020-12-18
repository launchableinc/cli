from .version import __version__
import click
import importlib
from os.path import dirname, basename, join
import glob
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

# load all test runners
for f in glob.glob(join(dirname(__file__), 'test_runners', "*.py")):
    f = basename(f)[:-3]
    if f=='__init__':
        continue
    m = importlib.import_module('launchable.test_runners.%s' % f)

if __name__ == '__main__':
    main()
