# cfgr

[![CI](https://github.com/egustafson/cfgr/actions/workflows/ci.yml/badge.svg)](https://github.com/egustafson/cfgr/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A configuration file manager and diff tool.

**Problem:** I want to keep *some* of my OS configuration files under
version control. The configuration file as placed in the OS is not in
a place where I want the entire directory under version control
(e.g. `/etc`).

**Strategy:** `cfgr` acts as the "go between", performing diff, push,
and pull functionality between a directory tree of managed configuration
files and the deployed location of those files.

## Installation

```sh
# Install with uv (recommended)
uv tool install cfgr

# Or with pip
pip install cfgr
```

## Usage

`cfgr` expects a `.cfgr.yml` configuration file in the working directory:

```yaml
target: /etc          # deployed location
source: ./source      # version-controlled source tree
ignore:
  - logs/
```

```sh
cfgr [--dir PATH] <command>

Commands:
  about      Print program information
  diff       Show differences between source and target
  pull       Pull changes from target into source
  push       Push changes from source to target
```

### diff options

| Option | Short | Description |
|--------|-------|-------------|
| `--short` | `-s` | List changed filenames only, no line-level diff |
| `--no-ignore` | `-I` | Include files that match ignore patterns |
| `--unified` | `-u` | Output unified diff format instead of side-by-side |
| `--nocolor` | | Disable colorized output (implied when stdout is not a TTY) |
| `--pager` | | Pipe output through `less` |

By default `cfgr diff` renders a colorized side-by-side diff when stdout is a
terminal. Color is automatically disabled when output is piped or redirected.
Use `--unified --nocolor` to reproduce plain unified diff output suitable for
scripting or patch files.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions.
