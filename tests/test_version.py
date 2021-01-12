from click.testing import CliRunner
from launchable.__main__ import main
from launchable.version import __version__
from nose.tools import eq_


def test_version():
    runner = CliRunner()
    result = runner.invoke(main, ['--version'])
    eq_(result.exit_code, 0)
    eq_(result.output, 'launchable-cli, version {}\n'.format(__version__))
