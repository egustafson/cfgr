import os
import shutil

from click.testing import CliRunner

from cfgr import cli

TEST_DATA = os.path.join(os.path.dirname(__file__), "..", "test_data")


def _setup(tmp_path):
    """Copy test_data into tmp_path and return the source dir path."""
    dest = tmp_path / "td"
    shutil.copytree(TEST_DATA, dest)
    src = str(dest / "source")
    # Rewrite .cfgr.yml with an absolute target path.
    abs_target = str(dest / "target")
    cfg = os.path.join(src, ".cfgr.yml")
    with open(cfg, "w") as f:
        f.write(f"target: {abs_target}\nignore:\n  - logs/\n")
    return src


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output


def test_about():
    runner = CliRunner()
    result = runner.invoke(cli, ["about"])
    assert result.exit_code == 0
    assert "0.10.0" in result.output


# ---------------------------------------------------------------------------
# diff
# ---------------------------------------------------------------------------


def test_diff_shows_diffs(tmp_path):
    wd = _setup(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "diff", "--unified", "--nocolor"])
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
    result = runner.invoke(cli, ["-d", wd, "diff", "-I", "--unified", "--nocolor"])
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


def test_diff_side_by_side(tmp_path):
    wd = _setup(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "diff", "--nocolor"])
    assert result.exit_code == 0
    assert "base.ini" in result.output
    assert "extension2.cfg" in result.output
    # In side-by-side mode, old and new values appear on the same output line
    assert any("debug" in line and "info" in line for line in result.output.splitlines())


def test_diff_unified_flag(tmp_path):
    wd = _setup(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "diff", "--unified", "--nocolor"])
    assert result.exit_code == 0
    assert "---" in result.output
    assert "+++" in result.output


def test_diff_nocolor_no_ansi(tmp_path):
    wd = _setup(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "diff", "--nocolor"])
    assert result.exit_code == 0
    assert "\x1b[" not in result.output


# ---------------------------------------------------------------------------
# child .cfgr.yml validation
# ---------------------------------------------------------------------------


def test_child_cfgr_invalid_target(tmp_path):
    wd = _setup(tmp_path)
    # Inject an illegal 'target' key into the child config
    child_cfg = os.path.join(wd, "subdir", ".cfgr.yml")
    with open(child_cfg, "w") as f:
        f.write("target: /some/path\n")
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "diff"])
    assert result.exit_code != 0
    assert "target" in result.output.lower()


# ---------------------------------------------------------------------------
# include
# ---------------------------------------------------------------------------


def test_include_limits_to_listed_file(tmp_path):
    wd = _setup(tmp_path)
    abs_target = os.path.normpath(os.path.join(wd, "..", "target"))
    cfg = os.path.join(wd, ".cfgr.yml")
    with open(cfg, "w") as f:
        f.write(f"target: {abs_target}\ninclude:\n  - base.ini\n")
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "diff", "-s"])
    assert result.exit_code == 0
    assert "base.ini" in result.output
    assert "extension2.cfg" not in result.output


def test_include_limits_to_listed_dir(tmp_path):
    wd = _setup(tmp_path)
    abs_target = os.path.normpath(os.path.join(wd, "..", "target"))
    cfg = os.path.join(wd, ".cfgr.yml")
    with open(cfg, "w") as f:
        f.write(f"target: {abs_target}\ninclude:\n  - subdir/\n")
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "diff", "-s"])
    assert result.exit_code == 0
    assert "extension2.cfg" in result.output
    assert "base.ini" not in result.output


def test_include_with_ignore(tmp_path):
    wd = _setup(tmp_path)
    abs_target = os.path.normpath(os.path.join(wd, "..", "target"))
    cfg = os.path.join(wd, ".cfgr.yml")
    with open(cfg, "w") as f:
        f.write(
            f"target: {abs_target}\ninclude:\n  - subdir/\nignore:\n  - subdir/extension2.cfg\n"
        )
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "diff", "-s"])
    assert result.exit_code == 0
    assert "extension2.cfg" not in result.output
    assert "base.ini" not in result.output


def test_child_include_limits_subdir(tmp_path):
    wd = _setup(tmp_path)
    # Add a second differing file in subdir so we can distinguish include from identity filtering
    with open(os.path.join(wd, "subdir", "extra.cfg"), "w") as f:
        f.write("extra=src\n")
    with open(os.path.join(wd, "..", "target", "subdir", "extra.cfg"), "w") as f:
        f.write("extra=tgt\n")
    child_cfg = os.path.join(wd, "subdir", ".cfgr.yml")
    with open(child_cfg, "w") as f:
        f.write("include:\n  - extension2.cfg\n")
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "diff", "-s"])
    assert result.exit_code == 0
    assert "extension2.cfg" in result.output
    assert "extra.cfg" not in result.output
    assert "base.ini" in result.output


# ---------------------------------------------------------------------------
# push
# ---------------------------------------------------------------------------


def test_push_copies_differing(tmp_path):
    wd = _setup(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "push"])
    assert result.exit_code == 0
    # After push, source and target base.ini must be identical
    src = os.path.join(wd, "base.ini")
    tgt = os.path.join(wd, "..", "target", "base.ini")
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
    src = os.path.join(wd, "base.ini")
    tgt = os.path.join(wd, "..", "target", "base.ini")
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
    src = os.path.join(wd, "base.ini")
    tgt = os.path.join(wd, "..", "target", "base.ini")
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
    src = os.path.join(wd, "base.ini")
    tgt = os.path.join(wd, "..", "target", "base.ini")
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


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------


def test_init_creates_config(tmp_path):
    src = str(tmp_path / "source")
    os.makedirs(src)
    tgt = str(tmp_path / "target")
    runner = CliRunner()
    result = runner.invoke(cli, ["init", tgt, "-D", src])
    assert result.exit_code == 0
    cfg = os.path.join(src, ".cfgr.yml")
    assert os.path.isfile(cfg)
    with open(cfg) as f:
        content = f.read()
    assert tgt in content


def test_init_default_source_dir(tmp_path):
    tgt = str(tmp_path / "target")
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path) as src:
        result = runner.invoke(cli, ["init", tgt])
        assert result.exit_code == 0
        assert os.path.isfile(os.path.join(src, ".cfgr.yml"))


def test_init_error_if_config_already_exists(tmp_path):
    src = str(tmp_path / "source")
    os.makedirs(src)
    cfg = os.path.join(src, ".cfgr.yml")
    with open(cfg, "w") as f:
        f.write("target: /tmp/existing\n")
    runner = CliRunner()
    result = runner.invoke(cli, ["init", "/tmp/target", "-D", src])
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_init_error_if_parent_has_config(tmp_path):
    parent = tmp_path / "repo"
    parent.mkdir()
    child = parent / "subdir"
    child.mkdir()
    # Place a .cfgr.yml in the parent
    (parent / ".cfgr.yml").write_text("target: /tmp/tgt\n")
    runner = CliRunner()
    result = runner.invoke(cli, ["init", "/tmp/target", "-D", str(child)])
    assert result.exit_code != 0
    assert ".cfgr.yml" in result.output


def test_init_error_if_target_is_relative(tmp_path):
    src = str(tmp_path / "source")
    os.makedirs(src)
    runner = CliRunner()
    result = runner.invoke(cli, ["init", "relative/path", "-D", src])
    assert result.exit_code != 0
    assert "absolute" in result.output.lower()


# ---------------------------------------------------------------------------
# hostname
# ---------------------------------------------------------------------------


def _setup_with_hostname(tmp_path, hostname):
    """Like _setup but writes hostname into .cfgr.yml."""
    wd = _setup(tmp_path)
    abs_target = os.path.normpath(os.path.join(wd, "..", "target"))
    cfg = os.path.join(wd, ".cfgr.yml")
    with open(cfg, "w") as f:
        f.write(f"target: {abs_target}\nhostname: {hostname}\nignore:\n  - logs/\n")
    return wd


def test_hostname_match_allows_diff(tmp_path):
    import socket

    wd = _setup_with_hostname(tmp_path, socket.gethostname())
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "diff", "-s"])
    assert result.exit_code == 0


def test_hostname_mismatch_warns_diff(tmp_path):
    wd = _setup_with_hostname(tmp_path, "no-such-host.example.invalid")
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "diff", "-s"])
    assert result.exit_code == 0
    assert "mismatch" in result.output.lower()


def test_hostname_mismatch_blocks_push(tmp_path):
    wd = _setup_with_hostname(tmp_path, "no-such-host.example.invalid")
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "push"])
    assert result.exit_code != 0
    assert "mismatch" in result.output.lower()


def test_hostname_mismatch_blocks_pull(tmp_path):
    wd = _setup_with_hostname(tmp_path, "no-such-host.example.invalid")
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "pull"])
    assert result.exit_code != 0
    assert "mismatch" in result.output.lower()


def test_hostname_mismatch_force_allows_push(tmp_path):
    wd = _setup_with_hostname(tmp_path, "no-such-host.example.invalid")
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "push", "--force", "base.ini"])
    assert result.exit_code == 0
    src = os.path.join(wd, "base.ini")
    tgt = os.path.normpath(os.path.join(wd, "..", "target", "base.ini"))
    with open(src) as f:
        src_content = f.read()
    with open(tgt) as f:
        tgt_content = f.read()
    assert src_content == tgt_content


def test_hostname_liberal_match_short_vs_fqdn(tmp_path):
    import socket

    current = socket.gethostname()
    short = current.split(".")[0]
    # Configure a FQDN when current may be short, or short when current is FQDN
    if "." in current:
        configured = short  # short should match FQDN current
    else:
        configured = current + ".example.local"  # FQDN should match short current
    wd = _setup_with_hostname(tmp_path, configured)
    runner = CliRunner()
    result = runner.invoke(cli, ["-d", wd, "diff", "-s"])
    assert result.exit_code == 0
