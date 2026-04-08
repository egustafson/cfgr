# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `diff` command: colorized side-by-side output by default when stdout is a terminal (via `ydiff>=1.5`)
- `diff --unified` / `-u`: output plain unified diff format instead of side-by-side
- `diff --nocolor`: disable ANSI color output regardless of TTY; color is automatically disabled when stdout is not a terminal
- `diff --pager` / `--no-pager`: opt-in to pipe output through `less` using ydiff's pager integration (default: off)
- `ops.render_diff()`: new function wrapping ydiff's `DiffParser`/`DiffMarker` API
- `ydiff>=1.5` runtime dependency

### Changed
- `diff` command default output changed from plain unified diff to colorized side-by-side; use `--unified --nocolor` for original plain behavior
- `README.md`: added `diff` options table and output-mode description

### Fixed
- Wrapped long `@click.option` decorator lines and `click.confirm` calls in `cfgr.py` to satisfy the 100-character line-length limit enforced by `ruff`
- Corrected import sort order in `ops.py` and `tests/test_cfgr.py` per `ruff` `I001` rules
- Added explicit `[tool.hatch.build.targets.wheel]` include list to `pyproject.toml` so that `context.py`, `filetree.py`, and `ops.py` are packaged alongside `cfgr.py`; previously only `cfgr.py` was included, causing `ModuleNotFoundError` when the tool was installed via `uv tool install`
- Fixed CI test failures: tests referenced `app.log` (a gitignored local-only file) rather than the committed `logfile.log`; updated `test_diff_no_ignore`, `test_diff_ignored_file_excluded_by_default`, and `test_diff_short_no_ignore` to assert against `logfile.log`

### Changed
- `Makefile`: `install` target updated to use `uv tool install .` (was `uv pip install .`)
- `Makefile`: added `pre-release` target (runs `lint` then `test`), `build` target (`uv build --wheel`), `dist` added to `clean`, and `clean`/`build` added to `.PHONY`
- `Makefile`: `clean` target now also removes `dist/`

### Added
- GitHub Actions `release` workflow (`.github/workflows/release.yml`): triggered on release publication; runs lint, tests, builds the wheel, and uploads it as a release asset

## [0.9.0] - 2026-04-07

### Added
- `diff` command with `-s`/`--short` (list changed files only) and `-I`/`--no-ignore` (bypass ignore patterns) options
- `push` command copies changed files from source to target; accepts explicit file paths and a `--force` flag (requires explicit paths); `--force` on an ignored file prompts to remove the ignore pattern from `.cfgr.yml`
- `pull` command mirrors `push` in the reverse direction (target → source) with the same options
- Support for child `.cfgr.yml` files in source subdirectories; child configs may add per-subdirectory `ignore` patterns and must not specify a `target` field (error raised if they do)
- `ops.py` module with shared utilities: `files_differ`, `unified_diff`, `get_tracked_pairs`, `copy_file`, `unignore_patterns`

### Changed
- `version` subcommand renamed to `about` (forward-compatible name for future program-info output)
- `context.py` refactored: child `.cfgr.yml` files are now loaded and their ignore patterns are combined with root-level patterns when determining which files to track
- Migrated project packaging from `setup.py` / `requirements.txt` to `pyproject.toml` using `uv` as the package manager
- Switched build backend to `hatchling`
- Updated `Makefile` targets to use `uv` commands; added `lint` target
- `version` command now reads version dynamically from package metadata
- Fixed `pathspec.PathSpec` construction bug in `context.py` (`PathSpec.from_lines` with `gitignore` pattern)
- Reformatted all source files with `ruff`
- CI runs on Python version pinned in `.python-version` (single runner, no matrix)

### Added
- `.python-version` file pinning Python 3.13
- `uv.lock` lockfile
- `tests/` directory with CLI smoke tests covering all commands
- GitHub Actions CI workflow (`.github/workflows/ci.yml`)
- `CONTRIBUTING.md` with dev setup, commit conventions, and PR guidelines
- `SECURITY.md` with vulnerability reporting policy
- `ruff` linter/formatter as a dev dependency
- `pytest` as a dev dependency
- Badges (CI, Python, License) in `README.md`
- Installation, usage, and development sections in `README.md`

### Removed
- `setup.py`
- `requirements.txt`

## [0.1.0] - 2026-04-06

### Added
- Initial release
- `cfgr` CLI entry point
- Diff, push, and pull functionality between managed config files and deployed locations

[Unreleased]: https://github.com/egustafson/cfgr/compare/v0.9.0...HEAD
[0.9.0]: https://github.com/egustafson/cfgr/compare/v0.1.0...v0.9.0
[0.1.0]: https://github.com/egustafson/cfgr/releases/tag/v0.1.0
