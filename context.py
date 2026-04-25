import os
import os.path

import click
import pathspec
from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

CFGR_CFG = ".cfgr.yml"


class CfgrCtx:
    def __init__(self, flags):
        self._verbose = flags.get("VERBOSE", 0) > 0
        self._force = flags.get("FORCE", False)
        self._dryrun = flags.get("DRYRUN", False)
        self._base_dir = flags.get("DIR", ".")
        os.chdir(self._base_dir)
        self._load_config()
        self._load_child_configs()
        self._root_matcher = pathspec.PathSpec.from_lines("gitignore", self._ignores)
        self._root_include_matcher = (
            pathspec.PathSpec.from_lines("gitignore", self._includes) if self._includes else None
        )

    def _load_config(self):
        # cwd is already changed to base_dir
        cfg_file = os.path.join(".", CFGR_CFG)
        with open(cfg_file) as f:
            cfg = load(f, Loader=Loader)
        self._target_dir = cfg["target"]
        if not os.path.isabs(self._target_dir):
            raise click.ClickException(
                f"'target' in {CFGR_CFG} must be an absolute path (got: '{self._target_dir}')."
            )
        self._source_dir = cfg.get("source", ".")
        self._ignores = cfg.get("ignore", [])
        self._includes = cfg.get("include", [])
        self._hostname = cfg.get("hostname", None)

    def _load_child_configs(self):
        """Walk source dir and load any child .cfgr.yml files."""
        self._child_matchers = {}
        self._child_include_matchers = {}
        for root, dirs, files in os.walk(self._source_dir):
            # Skip the root itself — only process subdirectories
            rel_root = os.path.relpath(root, self._source_dir)
            if rel_root == ".":
                continue
            if CFGR_CFG in files:
                cfg_path = os.path.join(root, CFGR_CFG)
                with open(cfg_path) as f:
                    cfg = load(f, Loader=Loader)
                if cfg and "target" in cfg:
                    raise click.ClickException(
                        f"Child config '{cfg_path}' must not contain a 'target' field."
                    )
                child_ignores = cfg.get("ignore", []) if cfg else []
                self._child_matchers[rel_root] = pathspec.PathSpec.from_lines(
                    "gitignore", child_ignores
                )
                child_includes = cfg.get("include", []) if cfg else []
                if child_includes:
                    self._child_include_matchers[rel_root] = pathspec.PathSpec.from_lines(
                        "gitignore", child_includes
                    )

    def is_ignored(self, rel_path):
        """Return True if rel_path (relative to source_dir) matches any ignore pattern."""
        # 1. Include list narrows the tracked set; if not matched, exclude.
        if self._root_include_matcher is not None and not self._root_include_matcher.match_file(
            rel_path
        ):
            return True
        # 2. Ignore list further reduces the tracked set.
        if self._root_matcher.match_file(rel_path):
            return True
        # Check each ancestor subdir for child matchers
        parts = rel_path.replace(os.sep, "/").split("/")
        for depth in range(1, len(parts)):
            subdir = os.path.join(*parts[:depth])
            ignore_matcher = self._child_matchers.get(subdir)
            include_matcher = self._child_include_matchers.get(subdir)
            if ignore_matcher is not None or include_matcher is not None:
                rel_to_subdir = os.path.join(*parts[depth:])
                if include_matcher is not None and not include_matcher.match_file(rel_to_subdir):
                    return True
                if ignore_matcher is not None and ignore_matcher.match_file(rel_to_subdir):
                    return True
        return False

    def _list_source_files(self):
        """Return source-relative paths of tracked (non-ignored) files."""
        result = []
        for root, dirs, files in os.walk(self._source_dir):
            rel_root = os.path.relpath(root, self._source_dir)
            for fname in files:
                if fname == CFGR_CFG:
                    continue
                if rel_root == ".":
                    rel_path = fname
                else:
                    rel_path = os.path.join(rel_root, fname)
                if not self.is_ignored(rel_path):
                    result.append(rel_path)
        return result

    def __str__(self):
        if self._base_dir != ".":
            return (
                f"{{ base: {self._base_dir}, target: {self.target_dir},"
                f" source: {self.source_dir}  }}"
            )
        else:
            return f"{{ target: {self.target_dir}, source: {self.source_dir}  }}"

    @property
    def verbose(self):
        return self._verbose

    @property
    def target_dir(self):
        return self._target_dir

    @property
    def source_dir(self):
        return self._source_dir

    @property
    def source_files(self):
        return self._list_source_files()

    @property
    def hostname(self):
        return self._hostname


def hostnames_match(config_host, current_host):
    """Return True if config_host and current_host refer to the same machine.

    Matching is liberal: if either name is a short hostname (no dots), only
    the first component of the other is compared.  Comparison is
    case-insensitive.
    """
    c = config_host.lower()
    h = current_host.lower()
    if c == h:
        return True
    return c.split(".")[0] == h.split(".")[0]
