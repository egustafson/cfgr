from click.testing import CliRunner

from cfgr import cli


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_diff():
    runner = CliRunner()
    result = runner.invoke(cli, ["diff"])
    assert result.exit_code == 0
    assert "diff" in result.output


def test_pull():
    runner = CliRunner()
    result = runner.invoke(cli, ["pull"])
    assert result.exit_code == 0
    assert "pull" in result.output


def test_push():
    runner = CliRunner()
    result = runner.invoke(cli, ["push"])
    assert result.exit_code == 0
    assert "push" in result.output


def test_dbg(tmp_path):
    import os
    import shutil

    # Copy test_data into a temp dir so dbg can find .cfgr.yml
    test_data = os.path.join(os.path.dirname(__file__), "..", "test_data")
    shutil.copytree(test_data, tmp_path / "td")

    runner = CliRunner()
    result = runner.invoke(cli, ["-d", str(tmp_path / "td"), "dbg"])
    assert result.exit_code == 0
    assert "target:" in result.output
