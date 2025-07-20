"""Open command implementation."""

import click
from .base import BaseCommand
from shelly.core.editor import Editor

@click.command()
@click.argument('repository')
@click.option('--editor', '-e', help='Specify editor to use')
def command(repository, editor):
    """Open repository in editor."""
    cmd = OpenCommand()
    cmd.execute(repository, editor)

class OpenCommand(BaseCommand):
    def execute(self, repository, editor=None):
        """Execute the open command."""
        editor_instance = Editor(editor or self.config.settings['editor'])
        editor_instance.open(repository)
