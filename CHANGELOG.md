# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.10.0] - 2026-04-24

### Added
- `include` field in `.cfgr.yml` (root and child configs): optional allowlist of gitignore-style patterns scoped to the target directory; when present, only matching files are tracked; `include` is evaluated before `ignore`
- Child `.cfgr.yml` files now support `include` in addition to `ignore`; patterns are matched relative to their subdirectory
- `init` command: initialises a new source directory by writing a `.cfgr.yml` with the given target path; accepts `-D` to specify the source directory; errors if a config already exists in the source dir or any ancestor directory
- `hostname` field in `.cfgr.yml` (optional): short or FQDN hostname; `diff` emits a warning on mismatch; `push` and `pull` abort on mismatch unless `--force` is given; matching is liberal (first hostname component only, case-insensitive)
- `target` field in `.cfgr.yml` must now be an absolute path; a relative path raises an error
- `diff` command: colorized side-by-side output by default when stdout is a terminal (via `ydiff>=1.5`)
- `diff --unified` / `-u`: output plain unified diff format instead of side-by-side
- `diff --nocolor`: disable ANSI color output regardless of TTY; color is automatically disabled when stdout is not a terminal
- `diff --pager` / `--no-pager`: opt-in to pipe output through `less` using ydiff's pager integration (default: off)
- `ops.render_diff()`: new function wrapping ydiff's `DiffParser`/`DiffMarker` API
- `ydiff>=1.5` runtime dependency
- GitHub Actions `release` workflow (`.github/workflows/release.yml`): triggered on release publication; runs lint, tests, builds the wheel, and uploads it as a release asset

### Changed
- `.cfgr.yml` is now expected to live **inside** the source directory; the containing directory is implicitly the source root — the `source` field has been removed
- `README.md`: added `.cfgr.yml` Reference section covering all fields, child configs, and pattern-precedence rules
- Minimum Python version raised from 3.8 to 3.10
- Dependency lower bounds updated: `click>=8.3.3`, `PyYAML>=6.0.3`, `pathspec>=1.1.0`; dev: `pytest>=9.0.3`, `ruff>=0.15.12`
- `diff` command default output changed from plain unified diff to colorized side-by-side; use `--unified --nocolor` for original plain behavior
- `Makefile`: `install` target updated to use `uv tool install .`; added `pre-release`, `build`, and updated `clean` targets

### Fixed
- Wrapped long `@click.option` decorator lines in `cfgr.py` to satisfy the 100-character line-length limit enforced by `ruff`
- Corrected import sort order in `ops.py` and `tests/test_cfgr.py` per `ruff` `I001` rules
- Added explicit `[tool.hatch.build.targets.wheel]` include list to `pyproject.toml` so that `context.py`, `filetree.py`, and `ops.py` are packaged alongside `cfgr.py`
- Fixed CI test failures caused by reference to gitignored `app.log`; updated tests to assert against `logfile.log`

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

[Unreleased]: https://github.com/egustafson/cfgr/compare/v0.10.0...HEAD
[0.10.0]: https://github.com/egustafson/cfgr/compare/v0.9.0...v0.10.0
[0.9.0]: https://github.com/egustafson/cfgr/compare/v0.1.0...v0.9.0
[0.1.0]: https://github.com/egustafson/cfgr/releases/tag/v0.1.0
