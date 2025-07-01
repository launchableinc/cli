import importlib
import importlib.util
import logging
import os
from glob import glob
from os.path import basename, dirname, join
from typing import Annotated, Optional

import typer

from smart_tests.app import Application
from smart_tests.commands.record.tests import create_nested_commands as create_record_target_commands
from smart_tests.commands.subset import create_nested_commands as create_subset_target_commands
from smart_tests.utils.test_runner_registry import get_registry

from .commands import inspect, record, split_subset, stats, subset, verify
from .utils import logger
from .utils.env_keys import SKIP_CERT_VERIFICATION
from .version import __version__

# Load all test runners at module level so they register their commands
for f in glob(join(dirname(__file__), 'test_runners', "*.py")):
    f = basename(f)[:-3]
    if f == '__init__':
        continue
    importlib.import_module('smart_tests.test_runners.%s' % f)

# Create initial NestedCommand commands with built-in test runners
try:
    create_subset_target_commands()
    create_record_target_commands()
except Exception as e:
    # If NestedCommand creation fails, continue with legacy commands
    # This ensures backward compatibility
    logging.warning(f"Failed to create NestedCommand commands at import time: {e}")
    pass

# Global flag to track if plugins have been loaded and commands need rebuilding
_plugins_loaded = False


def _rebuild_nested_commands_with_plugins():
    """Rebuild NestedCommand apps after plugins are loaded."""
    global _plugins_loaded
    if _plugins_loaded:
        return  # Already rebuilt

    try:
        # Clear existing commands from nested apps and rebuild
        for module_name in ['smart_tests.commands.subset', 'smart_tests.commands.record.tests']:
            module = importlib.import_module(module_name)
            if hasattr(module, 'nested_command_app'):
                nested_app = module.nested_command_app
                nested_app.registered_commands.clear()
                nested_app.registered_groups.clear()
            if hasattr(module, 'create_nested_commands'):
                module.create_nested_commands()

        _plugins_loaded = True
        logging.info("Successfully rebuilt NestedCommand apps with plugins")

    except Exception as e:
        logging.warning(f"Failed to rebuild NestedCommand apps with plugins: {e}")
        import traceback
        logging.warning(f"Traceback: {traceback.format_exc()}")


# Set up automatic rebuilding when new test runners are registered


def _on_test_runner_registered():
    """Callback triggered when new test runners are registered."""
    global _plugins_loaded
    if not _plugins_loaded:  # Only rebuild once for plugins
        _rebuild_nested_commands_with_plugins()


get_registry().set_on_register_callback(_on_test_runner_registered)

app = typer.Typer()


def version_callback(value: bool):
    if value:
        typer.echo(f"smart-tests-cli {__version__}")
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
        skip_cert_verification = (os.environ.get(SKIP_CERT_VERIFICATION) is not None)

    logging.basicConfig(level=level)

    # load all plugins
    if plugin_dir:
        for f in glob(join(plugin_dir, '*.py')):
            spec = importlib.util.spec_from_file_location(
                "smart_tests.plugins.{}".format(basename(f)[:-3]), f)
            if spec is None:
                raise ImportError(f"Failed to create module spec for plugin: {f}")
            if spec.loader is None:
                raise ImportError(f"Plugin spec has no loader: {f}")
            plugin = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin)

    # After loading plugins, rebuild NestedCommand apps to include plugin commands
    if plugin_dir:
        _rebuild_nested_commands_with_plugins()

    ctx.obj = Application(dry_run=dry_run, skip_cert_verification=skip_cert_verification)


# Use NestedCommand apps if available, otherwise fall back to legacy
try:
    from smart_tests.commands.record.tests import nested_command_app as record_target_app
    from smart_tests.commands.subset import nested_command_app as subset_target_app

    app.add_typer(record.app, name="record")
    app.add_typer(subset_target_app, name="subset")  # Use NestedCommand version
    app.add_typer(split_subset.app, name="split-subset")
    app.add_typer(verify.app, name="verify")
    app.add_typer(inspect.app, name="inspect")
    app.add_typer(stats.app, name="stats")

    # Add record-target as a sub-app to record command
    record.app.add_typer(record_target_app, name="test")  # Use NestedCommand version
except Exception as e:
    logging.warning(f"Failed to use NestedCommand apps at init: {e}")
    # Fallback to original structure
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
