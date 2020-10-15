from click.testing import CliRunner
from launchable.__main__ import main


def test_version():
    runner = CliRunner()
    result = runner.invoke(main, ['--version'])
    assert result.exit_code == 0
    assert result.output == 'launchable-cli, version 0.0.18\n'
