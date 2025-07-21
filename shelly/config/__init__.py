"""
Configuration management package
"""

from .manager import ConfigManager
from .settings import DEFAULT_CONFIG, SUPPORTED_EDITORS

__all__ = ["ConfigManager", "DEFAULT_CONFIG", "SUPPORTED_EDITORS"]
