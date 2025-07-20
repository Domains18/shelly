"""Interactive prompt functionality."""

import click

def confirm(message, default=True):
    """Prompt for confirmation."""
    return click.confirm(message, default=default)

def select(message, choices, default=0):
    """Prompt for selection from choices."""
    return click.prompt(
        message,
        type=click.Choice(choices),
        default=choices[default]
    )
