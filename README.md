# cfgr

[![CI](https://github.com/egustafson/cfgr/actions/workflows/ci.yml/badge.svg)](https://github.com/egustafson/cfgr/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
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

`cfgr` requires a `.cfgr.yml` configuration file inside the source directory
(the directory you pass to `--dir` or the current working directory):

```sh
cfgr [--dir PATH] <command>

Commands:
  about      Print program information
  diff       Show differences between source and target
  init       Initialise a new source directory with a .cfgr.yml
  pull       Pull changes from target into source
  push       Push changes from source to target
```

### init options

`cfgr init TARGET` creates a `.cfgr.yml` in the source directory pointing at
`TARGET`.  It is an error to initialise a directory that already contains a
`.cfgr.yml` or whose parent tree already contains one.

| Option | Description |
|--------|-------------|
| `TARGET` | Absolute path to the deployed (target) directory — recorded in `.cfgr.yml` |
| `-D PATH` | Source directory to initialise (default: current directory) |

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

## `.cfgr.yml` Reference

`cfgr` is configured by a `.cfgr.yml` file placed inside the **source
directory** (the directory you point `--dir` at, or the current working
directory). The directory that contains `.cfgr.yml` is implicitly the source
tree root.

### Root config (required)

```yaml
target: /etc          # path to the deployed location; must be an absolute path.

hostname: myhost      # optional — short or FQDN hostname of the machine this
                      # config is intended for.  diff emits a warning when the
                      # current hostname does not match; push and pull abort
                      # unless --force is given.  Matching is liberal: only the
                      # first hostname component is compared.

include:              # optional — allowlist of files/directories to track.
  - subdir/           # Entries are matched against target paths using
  - base.ini          # gitignore-style patterns (pathspec library).
                      # When omitted, all files are tracked.
                      # include is evaluated before ignore.

ignore:               # optional — denylist of files/directories to exclude.
  - logs/             # Same gitignore-style pattern matching.
  - "*.bak"           # Applied after include.
```

`target` is the only required field.  All others are optional.

### Child configs

Subdirectories of the source tree may contain their own `.cfgr.yml` files to
provide directory-scoped overrides.  Child configs support `include` and
`ignore`; the `target` field is **not allowed** and will cause an error.
Patterns in a child config are matched relative to that subdirectory.

```yaml
# source/subdir/.cfgr.yml
include:
  - "*.cfg"

ignore:
  - "*.bak"
```

### Pattern precedence

Filtering is applied in two passes:

1. **Include** — if an `include` list is present, only files matching those
   patterns are tracked; everything else is excluded.  If `include` is omitted,
   all files are implicitly included.  Child configs apply the same rule scoped
   to their subdirectory.
2. **Ignore** — files that match an `ignore` pattern are excluded from the
   tracked set, even if they were matched by `include`.  Child `ignore` patterns
   are resolved relative to their subdirectory.

Root-level patterns are evaluated before child-config patterns.
