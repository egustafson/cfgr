import os
import shutil

from click.testing import CliRunner

from cfgr import cli

TEST_DATA = os.path.join(os.path.dirname(__file__), "..", "test_data")


def _setup(tmp_path):
    """Copy test_data into tmp_path and return the working dir path."""
    dest = tmp_path / "td"
    shutil.copytree(TEST_DATA, dest)
    return str(dest)


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output


def test_about():
    runner = CliRunner()
    result = runner.invoke(cli, ["about"])
    assert result.exit_code == 0
    assert "0.9.0" in result.output


# ---------------------------------------------------------------------------
# diff
# ---------------------------------------------------------------------------


def test_diff_shows_diffs(tmp_path):
    wd = _setup(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "diff"])
    assert result.exit_code == 0
    # Both changed files should appear in unified diff output
    assert "base.ini" in result.output
    assert "extension2.cfg" in result.output
    # Unified diff markers
    assert "---" in result.output
    assert "+++" in result.output


def test_diff_short(tmp_path):
    wd = _setup(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "diff", "-s"])
    assert result.exit_code == 0
    assert "base.ini" in result.output
    assert "extension2.cfg" in result.output
    # Short mode must NOT contain unified diff markers
    assert "---" not in result.output
    assert "+++" not in result.output


def test_diff_no_ignore(tmp_path):
    wd = _setup(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "diff", "-I"])
    assert result.exit_code == 0
    # logs/logfile.log only appears when -I overrides ignore patterns
    assert "logfile.log" in result.output


def test_diff_ignored_file_excluded_by_default(tmp_path):
    wd = _setup(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "diff"])
    assert result.exit_code == 0
    # logs/logfile.log must be hidden by default ignore
    assert "logfile.log" not in result.output


def test_diff_identical_file_not_shown(tmp_path):
    wd = _setup(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "diff"])
    assert result.exit_code == 0
    assert "boilerplate.txt" not in result.output


def test_diff_short_no_ignore(tmp_path):
    wd = _setup(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "diff", "-s", "-I"])
    assert result.exit_code == 0
    assert "logfile.log" in result.output
    assert "---" not in result.output


# ---------------------------------------------------------------------------
# child .cfgr.yml validation
# ---------------------------------------------------------------------------


def test_child_cfgr_invalid_target(tmp_path):
    wd = _setup(tmp_path)
    # Inject an illegal 'target' key into the child config
    child_cfg = os.path.join(wd, "source", "subdir", ".cfgr.yml")
    with open(child_cfg, "w") as f:
        f.write("target: /some/path\n")
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "diff"])
    assert result.exit_code != 0
    assert "target" in result.output.lower()


# ---------------------------------------------------------------------------
# push
# ---------------------------------------------------------------------------


def test_push_copies_differing(tmp_path):
    wd = _setup(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "push"])
    assert result.exit_code == 0
    # After push, source and target base.ini must be identical
    src = os.path.join(wd, "source", "base.ini")
    tgt = os.path.join(wd, "target", "base.ini")
    with open(src) as f:
        src_content = f.read()
    with open(tgt) as f:
        tgt_content = f.read()
    assert src_content == tgt_content


def test_push_explicit_file(tmp_path):
    wd = _setup(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "push", "base.ini"])
    assert result.exit_code == 0
    src = os.path.join(wd, "source", "base.ini")
    tgt = os.path.join(wd, "target", "base.ini")
    with open(src) as f:
        src_content = f.read()
    with open(tgt) as f:
        tgt_content = f.read()
    assert src_content == tgt_content


def test_push_force_requires_files(tmp_path):
    wd = _setup(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "push", "--force"])
    assert result.exit_code != 0
    assert "force" in result.output.lower()


# ---------------------------------------------------------------------------
# pull
# ---------------------------------------------------------------------------


def test_pull_copies_differing(tmp_path):
    wd = _setup(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "pull"])
    assert result.exit_code == 0
    src = os.path.join(wd, "source", "base.ini")
    tgt = os.path.join(wd, "target", "base.ini")
    with open(src) as f:
        src_content = f.read()
    with open(tgt) as f:
        tgt_content = f.read()
    assert src_content == tgt_content


def test_pull_explicit_file(tmp_path):
    wd = _setup(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "pull", "base.ini"])
    assert result.exit_code == 0
    src = os.path.join(wd, "source", "base.ini")
    tgt = os.path.join(wd, "target", "base.ini")
    with open(src) as f:
        src_content = f.read()
    with open(tgt) as f:
        tgt_content = f.read()
    assert src_content == tgt_content


def test_pull_force_requires_files(tmp_path):
    wd = _setup(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "pull", "--force"])
    assert result.exit_code != 0
    assert "force" in result.output.lower()


# ---------------------------------------------------------------------------
# dbg (existing, now uses _setup helper)
# ---------------------------------------------------------------------------


def test_dbg(tmp_path):
    wd = _setup(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "dbg"])
    assert result.exit_code == 0
    assert "target:" in result.output
