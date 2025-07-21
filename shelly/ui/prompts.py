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

def select_from_list(message, choices, display_func=None):
    """Prompt for selection from a list with optional display transformation."""
    if display_func:
        display_choices = [display_func(choice) for choice in choices]
        choice_map = dict(zip(display_choices, choices))
        selected = click.prompt(
            message,
            type=click.Choice(display_choices)
        )
        return choice_map[selected]
    else:
        return click.prompt(
            message,
            type=click.Choice(choices)
        )

def confirm_action(message):
    """Prompt for confirmation of an action."""
    return click.confirm(message)
