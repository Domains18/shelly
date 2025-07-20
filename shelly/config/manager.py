"""Configuration manager for Shelly."""

import os
import yaml
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from .settings import DEFAULT_CONFIG, SUPPORTED_EDITORS
from .settings import DEFAULT_SETTINGS

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / '.shelly'
        self.config_file = self.config_dir / 'config.json'
        self.cache_file = self.config_dir / 'cache.json'


        self.config_dir.mkdir(exist_ok=True)

        self.config = self._load_config()
        self.cache = self._load_cache()

    def _load_config(self):
        """Load configuration from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    merged_config = DEFAULT_CONFIG.copy()
                    merged_config.update(config)
                    return merged_config
                
            except (json.JSONDecodeError, IOError):
                pass

        return DEFAULT_CONFIG.copy()
    

    def load_cache(self) -> Dict[str, Any]:
        """load cache from file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}