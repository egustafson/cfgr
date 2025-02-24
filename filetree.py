# -*- mode: python; coding: utf-8 -*-

import pathlib
import os
import os.path


class FileTree:

    def __init__(self, trunk):
        self._trunk = trunk
        fl = []
        for root, _, files in os.walk(trunk):
            for f in files:
                fl.append(os.path.normpath(os.path.join(root, f)))
        self._tree = fl

    def __str__(self):
        return f"{{ trunk: {self._trunk}, files: {len(self._tree)} }}"