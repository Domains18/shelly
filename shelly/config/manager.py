"""Configuration manager for Shelly."""

import os
import yaml
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from .settings import DEFAULT_CONFIG, SUPPORTED_EDITORS
from .settings import DEFAULT_SETTINGS

class ConfigManager:
    def __init__(self, config_path=None):
        self.config_path = config_path or os.path.expanduser("~/.config/shelly/config.yml")
        self.settings = self._load_config()

    def _load_config(self):
        """Load configuration from file or create default."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return {**DEFAULT_SETTINGS, **yaml.safe_load(f)}
        return DEFAULT_SETTINGS.copy()

    def save(self):
        """Save current configuration to file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(self.settings, f)
