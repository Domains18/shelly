"""List command implementation."""

import click
from .base import BaseCommand
from shelly.core.repository import Repository

@click.command()
@click.option('--filter', '-f', help='Filter repositories')
def command(filter):
    """List managed repositories."""
    cmd = ListCommand()
    cmd.execute(filter)

class ListCommand(BaseCommand):
    def execute(self, filter=None):
        """Execute the list command."""
        repos = Repository.list_all()
        if filter:
            repos = [r for r in repos if filter in r.name]
        for repo in repos:
            click.echo(repo)
