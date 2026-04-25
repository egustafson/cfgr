import os
import socket
import sys
import types
from importlib.metadata import version as pkg_version

import click
import ydiff

import context
import filetree
import ops


@click.group()
@click.option("-v", "--verbose", count=True)
@click.option(
    "-d", "--dir", default=".", type=click.Path(exists=True, file_okay=False, executable=True)
)
@click.pass_context
def cli(ctx, verbose, dir):
    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose
    ctx.obj["DIR"] = dir


def _check_hostname(cx, force=False, warn_only=False):
    """Warn on hostname mismatch; abort if not force (unless warn_only)."""
    if cx.hostname is None:
        return
    current = socket.gethostname()
    if not context.hostnames_match(cx.hostname, current):
        msg = f"Hostname mismatch: config expects '{cx.hostname}', current host is '{current}'."
        if warn_only or force:
            click.echo(f"Warning: {msg}", err=True)
        else:
            raise click.ClickException(msg + " Use --force to override.")


@click.command()
def about():
    click.echo(pkg_version("cfgr"))


@click.command()
@click.option(
    "--short", "-s", is_flag=True, help="List differing files without showing line changes."
)
@click.option("--no-ignore", "-I", is_flag=True, help="Include files that match ignore patterns.")
@click.option(
    "--unified", "-u", is_flag=True, help="Output unified diff format instead of side-by-side."
)
@click.option("--nocolor", is_flag=True, help="Disable colorized output.")
@click.option("--pager/--no-pager", default=False, help="Pipe output through less.")
@click.pass_context
def diff(ctx, short, no_ignore, unified, nocolor, pager):
    cx = context.CfgrCtx(ctx.obj)
    _check_hostname(cx, warn_only=True)
    pairs = ops.get_tracked_pairs(cx, no_ignore=no_ignore)
    use_color = sys.stdout.isatty() and not nocolor
    if pager and sys.stdout.isatty() and use_color:
        # Collect all unified diff text and feed to ydiff's pager
        all_lines = []
        for abs_src, abs_tgt, rel in pairs:
            if ops.files_differ(abs_src, abs_tgt):
                text = ops.unified_diff(abs_src, abs_tgt, label_src=rel, label_tgt=rel)
                if text:
                    all_lines.extend(
                        line.encode("utf-8") for line in text.splitlines(keepends=True)
                    )
        if all_lines:
            opts = types.SimpleNamespace(
                side_by_side=not unified,
                width=0,
                wrap=True,
                theme="default",
                tab_width=8,
                pager=None,
                pager_options=None,
            )
            ydiff.markup_to_pager(iter(all_lines), opts)
    else:
        for abs_src, abs_tgt, rel in pairs:
            if ops.files_differ(abs_src, abs_tgt):
                if short:
                    click.echo(rel)
                else:
                    output = ops.render_diff(
                        abs_src,
                        abs_tgt,
                        side_by_side=(not unified),
                        color=use_color,
                        label_src=rel,
                        label_tgt=rel,
                    )
                    if output:
                        click.echo(output, nl=False)


@click.command()
@click.option(
    "--force", is_flag=True, help="Copy files unconditionally. Requires explicit file paths."
)
@click.argument("files", nargs=-1)
@click.pass_context
def pull(ctx, force, files):
    if force and not files:
        raise click.UsageError("--force requires explicit file paths.")
    cx = context.CfgrCtx(ctx.obj)
    _check_hostname(cx, force=force)
    if files:
        pairs = []
        for f in files:
            abs_src = os.path.join(cx.source_dir, f)
            abs_tgt = os.path.join(cx.target_dir, f)
            pairs.append((abs_src, abs_tgt, f))
    else:
        pairs = ops.get_tracked_pairs(cx)
    for abs_src, abs_tgt, rel in pairs:
        should_copy = force or ops.files_differ(abs_src, abs_tgt)
        if should_copy:
            if not os.path.isfile(abs_tgt):
                continue
            if force and cx.is_ignored(rel):
                msg = f"'{rel}' matches an ignore pattern. Remove from .cfgr.yml ignore list?"
                if click.confirm(msg):
                    ops.unignore_patterns(".cfgr.yml", [rel])
            ops.copy_file(abs_tgt, abs_src)
            if cx.verbose:
                click.echo(f"pulled: {rel}")


@click.command()
@click.option(
    "--force", is_flag=True, help="Copy files unconditionally. Requires explicit file paths."
)
@click.argument("files", nargs=-1)
@click.pass_context
def push(ctx, force, files):
    #
    # - check for write permissions early
    # - stash any changes for a rollback.
    #
    if force and not files:
        raise click.UsageError("--force requires explicit file paths.")
    cx = context.CfgrCtx(ctx.obj)
    _check_hostname(cx, force=force)
    if files:
        pairs = []
        for f in files:
            abs_src = os.path.join(cx.source_dir, f)
            abs_tgt = os.path.join(cx.target_dir, f)
            pairs.append((abs_src, abs_tgt, f))
    else:
        pairs = ops.get_tracked_pairs(cx)
    for abs_src, abs_tgt, rel in pairs:
        if force or ops.files_differ(abs_src, abs_tgt):
            if not os.path.isfile(abs_src):
                continue
            if force and cx.is_ignored(rel):
                msg = f"'{rel}' matches an ignore pattern. Remove from .cfgr.yml ignore list?"
                if click.confirm(msg):
                    ops.unignore_patterns(".cfgr.yml", [rel])
            ops.copy_file(abs_src, abs_tgt)
            if cx.verbose:
                click.echo(f"pushed: {rel}")


@click.command()
@click.argument("target", type=click.Path())
@click.option(
    "-D",
    "--source-dir",
    default=".",
    type=click.Path(exists=True, file_okay=False),
    help="Source directory to initialise (default: current directory).",
)
def init(target, source_dir):
    """Initialise a new .cfgr.yml in the source directory pointing at TARGET."""
    if not os.path.isabs(target):
        raise click.UsageError("TARGET must be an absolute path.")
    source_dir = os.path.abspath(source_dir)
    cfg_path = os.path.join(source_dir, context.CFGR_CFG)

    if os.path.isfile(cfg_path):
        raise click.ClickException(f"'{cfg_path}' already exists.")

    # Walk up through parent directories — none may contain a .cfgr.yml.
    parent = os.path.dirname(source_dir)
    while True:
        if os.path.isfile(os.path.join(parent, context.CFGR_CFG)):
            raise click.ClickException(
                f"Parent directory '{parent}' already contains a {context.CFGR_CFG}."
            )
        next_parent = os.path.dirname(parent)
        if next_parent == parent:
            break
        parent = next_parent

    from yaml import dump

    try:
        from yaml import CDumper as Dumper
    except ImportError:
        from yaml import Dumper

    with open(cfg_path, "w") as f:
        dump({"target": target}, f, Dumper=Dumper, default_flow_style=False)
    click.echo(f"Initialized {cfg_path}")


@click.command(hidden=True)
@click.pass_context
def dbg(ctx):
    click.echo("debug:")
    cx = context.CfgrCtx(ctx.obj)
    click.echo(cx)
    click.echo("source files:")
    for sf in cx.source_files:
        click.echo(f"  {sf}")

    tgttree = filetree.FileTree(cx.target_dir)
    click.echo(f"tgt: {tgttree}")


cli.add_command(about)
cli.add_command(diff)
cli.add_command(init)
cli.add_command(pull)
cli.add_command(push)
cli.add_command(dbg)

if __name__ == "__main__":
    cli()
