# -*- mode: python; coding: utf-8 -*-

import click

@click.group()
def cli():
    pass

@click.command()
def version():
    click.echo("v0.Unknown")

@click.command()
def diff():
    click.echo("diff -- wip")

@click.command()
def pull():
    click.echo("pull -- wip")

@click.command()
def push():
    #
    # - check for write permissions early
    # - stash any changes for a rollback.
    #
    click.echo("push -- wip")

cli.add_command(version)
cli.add_command(diff)
cli.add_command(pull)
cli.add_command(push)

if __name__ == '__main__':
    cli()
