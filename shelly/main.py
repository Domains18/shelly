"""Main entry point for the Shelly CLI."""

import click
from shelly.commands import clone, config, list_cmd, open_cmd

@click.group()
@click.version_option()
def main():
    """Shelly - A shell utility for managing development environments."""
    pass

# Register commands
main.add_command(clone.command)
main.add_command(config.command)
main.add_command(list_cmd.command)
main.add_command(open_cmd.command)

if __name__ == '__main__':
    main()
