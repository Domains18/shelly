"""Base command class for Shelly CLI commands."""

import click
from shelly.config import ConfigManager

class BaseCommand:
    def __init__(self):
        self.config = ConfigManager()

    def get_context(self):
        """Get command context with configuration."""
        return {'config': self.config}
