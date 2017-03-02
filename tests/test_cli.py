from click.testing import CliRunner

from shakedown import *
from dcos import config

def test_cli_require_dcos_uri():
    runner = CliRunner()
    result = runner.invoke(cli.main.cli)
    # with preconfigured dcos cli dcos url isn't required
    assert '--dcos-url is a required option' not in result.output
    # oddly results -1
    assert result.exit_code == -1

    with dcos_config():
        config.unset('core.dcos_url')
        result = runner.invoke(cli.main.cli)
        assert '--dcos-url is a required option' in result.output
        assert result.exit_code == 1


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli.main.cli, ['--version'])
    assert result.exit_code == 0
    assert result.output == "shakedown, version " + shakedown.VERSION + "\n"
    print(result.output)
