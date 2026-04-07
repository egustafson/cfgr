# -*- mode: Makefile -*-

.PHONY: dev_install install init test lint

install:
	uv pip install .

dev_install:
	uv sync

init:
	uv sync

test:
	uv run pytest tests

lint:
	uv run ruff check . && uv run ruff format --check .

clean:
	-rm -rf cfgr.egg-info __pycache__ .venv
