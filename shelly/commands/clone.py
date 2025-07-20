"""Clone command implementation."""

import click
from .base import BaseCommand
from shelly.core.repository import Repository

@click.command()
@click.argument('repository')
@click.option('--path', '-p', help='Custom clone path')
def command(repository, path):
    """Clone a repository."""
    cmd = CloneCommand()
    cmd.execute(repository, path)

class CloneCommand(BaseCommand):
    def execute(self, repository, path=None):
        """Execute the clone command."""
        repo = Repository(repository)
        repo.clone(path)
