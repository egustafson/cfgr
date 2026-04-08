import difflib
import os
import os.path
import re
import shutil

from yaml import dump, load

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Dumper, Loader

CFGR_CFG = ".cfgr.yml"


def files_differ(src_path, tgt_path):
    """Return True if the two files have different byte content or one is missing."""
    src_exists = os.path.isfile(src_path)
    tgt_exists = os.path.isfile(tgt_path)
    if src_exists != tgt_exists:
        return True
    if not src_exists:
        return False
    with open(src_path, "rb") as f:
        src_bytes = f.read()
    with open(tgt_path, "rb") as f:
        tgt_bytes = f.read()
    return src_bytes != tgt_bytes


def unified_diff(src_path, tgt_path, label_src=None, label_tgt=None):
    """Return a unified diff string comparing src to tgt."""
    label_src = label_src or src_path
    label_tgt = label_tgt or tgt_path

    def read_lines(path):
        if not os.path.isfile(path):
            return []
        with open(path, errors="replace") as f:
            return f.readlines()

    src_lines = read_lines(src_path)
    tgt_lines = read_lines(tgt_path)
    lines = list(difflib.unified_diff(src_lines, tgt_lines, fromfile=label_src, tofile=label_tgt))
    return "".join(lines)


def render_diff(
    src_path, tgt_path, *, side_by_side=True, color=True, label_src=None, label_tgt=None
):
    """Return a rendered diff string using ydiff.

    side_by_side=True renders a side-by-side layout; False renders unified format.
    color=True includes ANSI color codes; False strips them.
    Returns an empty string when the files are identical or both absent.
    """
    import ydiff

    text = unified_diff(src_path, tgt_path, label_src=label_src, label_tgt=label_tgt)
    if not text:
        return ""

    stream = [line.encode("utf-8") for line in text.splitlines(keepends=True)]
    marker = ydiff.DiffMarker(side_by_side=side_by_side, width=0, wrap=True)
    parts = []
    for diff in ydiff.DiffParser(stream).parse():
        for line in marker.markup(diff):
            parts.append(line)
    result = "".join(parts)
    if not color:
        result = re.sub(r"\x1b\[[0-9;]*m", "", result)
    return result


def get_tracked_pairs(cx, no_ignore=False):
    """Return (abs_src, abs_tgt, rel_path) triples for the union of source and target files.

    Files matching ignore patterns are excluded unless no_ignore=True.
    """
    src_root = cx.source_dir
    tgt_root = cx.target_dir

    seen = set()
    pairs = []

    # Collect from source tree
    for root, dirs, files in os.walk(src_root):
        rel_root = os.path.relpath(root, src_root)
        for fname in files:
            if fname == CFGR_CFG:
                continue
            rel = fname if rel_root == "." else os.path.join(rel_root, fname)
            if not no_ignore and cx.is_ignored(rel):
                continue
            seen.add(rel)
            abs_src = os.path.join(src_root, rel)
            abs_tgt = os.path.join(tgt_root, rel)
            pairs.append((abs_src, abs_tgt, rel))

    # Collect files that exist only in the target tree
    for root, dirs, files in os.walk(tgt_root):
        rel_root = os.path.relpath(root, tgt_root)
        for fname in files:
            rel = fname if rel_root == "." else os.path.join(rel_root, fname)
            if rel in seen:
                continue
            if not no_ignore and cx.is_ignored(rel):
                continue
            abs_src = os.path.join(src_root, rel)
            abs_tgt = os.path.join(tgt_root, rel)
            pairs.append((abs_src, abs_tgt, rel))

    return sorted(pairs, key=lambda t: t[2])


def copy_file(src, dst):
    """Copy src to dst, creating any necessary parent directories."""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


def unignore_patterns(cfg_path, patterns):
    """Remove matching entries from the ignore list in a .cfgr.yml and rewrite it."""
    with open(cfg_path) as f:
        cfg = load(f, Loader=Loader) or {}
    ignores = cfg.get("ignore", [])
    new_ignores = [p for p in ignores if p not in patterns]
    cfg["ignore"] = new_ignores
    with open(cfg_path, "w") as f:
        dump(cfg, f, Dumper=Dumper, default_flow_style=False)
