# -*- mode: python; coding: utf-8 -*-

import os
import os.path
import pathspec

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

CFGR_CFG = ".cfgr.yml"


class CfgrCtx:

    def __init__(self, flags):
        self._verbose = (flags.get('VERBOSE', 0) > 0)
        self._force = flags.get('FORCE', False)
        self._dryrun = flags.get('DRYRUN', False)
        self._base_dir = flags.get('DIR', '.')
        os.chdir(self._base_dir)
        self._load_config()
        self._ignore_matcher = pathspec.PathSpec(self._ignores)
        self._source_files = self._ignore_matcher.match_tree_entries(self._source_dir)

    def _load_config(self):
        # cwd is already changed to base_dir
        cfg_file = os.path.join('.', CFGR_CFG)
        with open(cfg_file) as f:
            cfg = load(f, Loader=Loader)
        self._target_dir = cfg['target']
        self._source_dir = cfg.get('source', '.')
        self._ignores = cfg.get('ignore', [])

    def __str__(self):
        if self._base_dir != ".":
            return f"{{ base: {self._base_dir}, target: {self.target_dir}, source: {self.source_dir}  }}"
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
        return self._source_files