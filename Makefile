# -*- mode: Makefile -*-

.PHONY: dev_install install init test lint pre-release build clean

install:
	uv tool install .

dev_install:
	uv sync

init:
	uv sync

pre-release: lint test

build:
	uv build --wheel

test:
	uv run pytest tests

lint:
	uv run ruff check . && uv run ruff format --check .

clean:
	-rm -rf cfgr.egg-info __pycache__ .venv dist
