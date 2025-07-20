"""Tests for repository functionality."""

import pytest
from shelly.core.repository import Repository
from shelly.core.utils import validate_url

def test_repository_init():
    """Test repository initialization."""
    url = "https://github.com/username/repo.git"
    repo = Repository(url)
    assert repo.name == "repo"
    assert repo.url == url

def test_validate_url():
    """Test URL validation."""
    valid_urls = [
        "https://github.com/username/repo.git",
        "git@github.com:username/repo.git"
    ]
    invalid_urls = [
        "not_a_url",
        "https://not-github.com/user/repo.git"
    ]
    
    for url in valid_urls:
        assert validate_url(url)
    for url in invalid_urls:
        assert not validate_url(url)
