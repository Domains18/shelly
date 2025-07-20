"""Tests for configuration functionality."""

import pytest
from shelly.config import ConfigManager, DEFAULT_SETTINGS

def test_config_load_defaults():
    """Test loading default configuration."""
    config = ConfigManager()
    assert config.settings == DEFAULT_SETTINGS

def test_config_save_load():
    """Test saving and loading configuration."""
    config = ConfigManager()
    config.settings['test_key'] = 'test_value'
    config.save()
    
    new_config = ConfigManager()
    assert new_config.settings['test_key'] == 'test_value'
