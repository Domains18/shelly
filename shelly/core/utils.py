"""Utility functions for Shelly."""

import os
import re
from shelly.config import ConfigManager

def get_repo_path(name):
    """Get the full path for a repository."""
    config = ConfigManager()
    base_path = os.path.expanduser(config.settings['repos_path'])
    return os.path.join(base_path, name)

def validate_url(url):
    """Validate repository URL format."""
    patterns = [
        r'^https://github\.com/[\w-]+/[\w-]+(?:\.git)?$',
        r'^git@github\.com:[\w-]+/[\w-]+(?:\.git)?$'
    ]
    return any(re.match(pattern, url) for pattern in patterns)
