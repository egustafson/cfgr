# Contributing to cfgr

## Development Setup

Requires [uv](https://docs.astral.sh/uv/).

```sh
git clone https://github.com/egustafson/cfgr.git
cd cfgr
uv sync        # creates .venv and installs all dependencies
```

## Running Tests

```sh
make test
# or directly:
uv run pytest tests
```

## Linting and Formatting

```sh
make lint             # check for issues
uv run ruff format .  # auto-format
```

## Commit Convention

This project follows [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — new feature
- `fix:` — bug fix
- `chore:` — maintenance (deps, tooling)
- `docs:` — documentation only
- `test:` — test additions or changes
- `refactor:` — code change that neither fixes a bug nor adds a feature

## Pull Requests

1. Fork the repo and create a branch from `main`
2. Add tests for any new behaviour
3. Ensure `make test` and `make lint` both pass
4. Update [CHANGELOG.md](CHANGELOG.md) under `[Unreleased]`
5. Open a PR against `main`

## Reporting Issues

Use [GitHub Issues](https://github.com/egustafson/cfgr/issues).
For security vulnerabilities, see [SECURITY.md](SECURITY.md).
