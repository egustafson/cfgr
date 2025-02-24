# -*- mode: python; coding: utf-8 -*-

import os
import os.path

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

CFGR_CFG = ".cfgr.yml"


class CfgrCtx:

    def __init__(self, flags):
        self._verbose = (flags.get('VERBOSE', 0) > 0)
        self._base_dir = flags.get('DIR', '.')
        os.chdir(self._base_dir)
        self._load_config()

    def _load_config(self):
        # cwd is already changed to base_dir
        cfg_file = os.path.join('.', CFGR_CFG)
        with open(cfg_file) as f:
            cfg = load(f, Loader=Loader)
        self._target = cfg['target']
        self._source = cfg.get('source', '.')
        self._ignores = cfg.get('ignore', [])
        self._includes = cfg.get('include', [])

    def __str__(self):
        if self._base_dir != ".":
            return f"{{ base: {self._base_dir}, target: {self.target}, source: {self.source}  }}"
        else:
            return f"{{ target: {self.target}, source: {self.source}  }}"

    @property
    def verbose(self):
        return self._verbose
    
    @property
    def target(self):
        return self._target
    
    @property
    def source(self):
        return self._source
    
    @property
    def ignores(self):
        return self._ignores
    
    @property
    def includes(self):
        return self._includes