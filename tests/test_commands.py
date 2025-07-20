"""Tests for CLI commands."""

import pytest
from click.testing import CliRunner
from shelly.main import main

def test_version():
    """Test version command."""
    runner = CliRunner()
    result = runner.invoke(main, ['--version'])
    assert result.exit_code == 0

def test_config_command():
    """Test config command."""
    runner = CliRunner()
    
    # Test getting all config
    result = runner.invoke(main, ['config'])
    assert result.exit_code == 0
    
    # Test setting config value
    result = runner.invoke(main, ['config', 'test_key', 'test_value'])
    assert result.exit_code == 0
    
    # Test getting specific config value
    result = runner.invoke(main, ['config', 'test_key'])
    assert result.exit_code == 0
    assert result.output.strip() == 'test_value'
