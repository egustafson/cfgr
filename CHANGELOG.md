# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
