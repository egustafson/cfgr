# -*- mode: python; coding: utf-8 -*-

import click

import context
import filetree


@click.group()
@click.option('-v', '--verbose', count=True)
@click.option('-d', '--dir', default=".",
              type=click.Path(exists=True,
                              file_okay=False,
                              executable=True))
@click.pass_context
def cli(ctx, verbose, dir):
    ctx.ensure_object(dict)
    ctx.obj['VERBOSE'] = verbose
    ctx.obj['DIR'] = dir


@click.command()
def version():
    click.echo("v0.Unknown")


@click.command()
@click.pass_context
def diff(ctx):
    click.echo("diff -- wip")


@click.command()
@click.pass_context
def pull(ctx):
    click.echo("pull -- wip")


@click.command()
@click.pass_context
def push(ctx):
    #
    # - check for write permissions early
    # - stash any changes for a rollback.
    #
    click.echo("push -- wip")


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


cli.add_command(version)
cli.add_command(diff)
cli.add_command(pull)
cli.add_command(push)
cli.add_command(dbg)

if __name__ == '__main__':
    cli()
