"""Config command implementation."""

import click
from .base import BaseCommand

@click.command()
@click.argument('key', required=False)
@click.argument('value', required=False)
def command(key, value):
    """Get or set configuration values."""
    cmd = ConfigCommand()
    cmd.execute(key, value)

class ConfigCommand(BaseCommand):
    def execute(self, key=None, value=None):
        """Execute the config command."""
        if key and value:
            self.config.settings[key] = value
            self.config.save()
        elif key:
            click.echo(self.config.settings.get(key))
        else:
            click.echo(self.config.settings)
