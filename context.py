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

    def _load_config(self):
        # cwd is already changed to base_dir
        cfg_file = os.path.join(".", CFGR_CFG)
        with open(cfg_file) as f:
            cfg = load(f, Loader=Loader)
        self._target_dir = cfg["target"]
        self._source_dir = cfg.get("source", ".")
        self._ignores = cfg.get("ignore", [])

    def _load_child_configs(self):
        """Walk source dir and load any child .cfgr.yml files."""
        self._child_matchers = {}
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

    def is_ignored(self, rel_path):
        """Return True if rel_path (relative to source_dir) matches any ignore pattern."""
        if self._root_matcher.match_file(rel_path):
            return True
        # Check each ancestor subdir for child matchers
        parts = rel_path.replace(os.sep, "/").split("/")
        for depth in range(1, len(parts)):
            subdir = os.path.join(*parts[:depth])
            matcher = self._child_matchers.get(subdir)
            if matcher is not None:
                # path relative to that subdir
                rel_to_subdir = os.path.join(*parts[depth:])
                if matcher.match_file(rel_to_subdir):
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
