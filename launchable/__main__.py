import importlib
import importlib.util
import logging
import os
from glob import glob
from os.path import basename, dirname, join
from typing import Annotated, Optional

import typer

from launchable.app import Application

from .commands import inspect, record, split_subset, stats, subset, verify
from .utils import logger
from .version import __version__

# Load all test runners at module level so they register their commands
for f in glob(join(dirname(__file__), 'test_runners', "*.py")):
    f = basename(f)[:-3]
    if f == '__init__':
        continue
    importlib.import_module('launchable.test_runners.%s' % f)

app = typer.Typer()


def version_callback(value: bool):
    if value:
        typer.echo(f"launchable-cli {__version__}")
        raise typer.Exit()


def main(
    ctx: typer.Context,
    log_level: Annotated[str, typer.Option(
        help="Set logger's log level (CRITICAL, ERROR, WARNING, AUDIT, INFO, DEBUG)."
    )] = logger.LOG_LEVEL_DEFAULT_STR,
    plugin_dir: Annotated[Optional[str], typer.Option(
        "--plugin-dir", "--plugins",
        help="Directory to load plugins from"
    )] = None,
    dry_run: Annotated[bool, typer.Option(
        help="Dry-run mode. No data is sent to the server. However, sometimes "
             "GET requests without payload data or side effects could be sent."
             "note: Since the dry run log is output together with the AUDIT log, "
             "even if the log-level is set to warning or higher, the log level will "
             "be forced to be set to AUDIT."
    )] = False,
    skip_cert_verification: Annotated[bool, typer.Option(
        help="Skip the SSL certificate check. This lets you bypass system setup issues "
             "like CERTIFICATE_VERIFY_FAILED, at the expense of vulnerability against "
             "a possible man-in-the-middle attack. Use it as an escape hatch, but with caution."
    )] = False,
    version: Annotated[Optional[bool], typer.Option(
        "--version", help="Show version and exit", callback=version_callback, is_eager=True
    )] = None,
):

    level = logger.get_log_level(log_level)
    # In the case of dry-run, it is forced to set the level below the AUDIT.
    # This is because the dry-run log will be output along with the audit log.
    if dry_run and level > logger.LOG_LEVEL_AUDIT:
        level = logger.LOG_LEVEL_AUDIT

    if not skip_cert_verification:
        skip_cert_verification = (os.environ.get('LAUNCHABLE_SKIP_CERT_VERIFICATION') is not None)

    logging.basicConfig(level=level)

    # load all plugins
    if plugin_dir:
        for f in glob(join(plugin_dir, '*.py')):
            spec = importlib.util.spec_from_file_location(
                "launchable.plugins.{}".format(basename(f)[:-3]), f)
            if spec is None:
                raise ImportError(f"Failed to create module spec for plugin: {f}")
            if spec.loader is None:
                raise ImportError(f"Plugin spec has no loader: {f}")
            plugin = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin)

    ctx.obj = Application(dry_run=dry_run, skip_cert_verification=skip_cert_verification)


app.add_typer(record.app, name="record")
app.add_typer(subset.app, name="subset")
app.add_typer(split_subset.app, name="split-subset")
app.add_typer(verify.app, name="verify")
app.add_typer(inspect.app, name="inspect")
app.add_typer(stats.app, name="stats")

app.callback()(main)

# For backward compatibility with tests that expect a Click CLI
# We'll need to use Typer's testing utilities instead
main = app

if __name__ == '__main__':
    app()
