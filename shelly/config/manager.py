"""Configuration manager for Shelly."""

import os
import yaml
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from .settings import DEFAULT_CONFIG, SUPPORTED_EDITORS
from .settings import DEFAULT_CONFIG as DEFAULT_SETTINGS, SUPPORTED_EDITORS

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / '.shelly'
        self.config_file = self.config_dir / 'config.json'
        self.cache_file = self.config_dir / 'cache.json'


        self.config_dir.mkdir(exist_ok=True)

        self.config = self._load_config()
        self.cache = self.load_cache()

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


    def save_config(self) -> None:
        """save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2, sort_keys=True)
        except IOError as e:
            raise Exception(f"failed to save configuration: {e}")
        

    def save_cache(self) -> None:
        """save cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2, sort_keys=True)

        except IOError as e:
            raise Exception(f"failed to save cache {e}")
        

    def get_base_dir(self) -> Optional[Path]:
        """set the base dir for cloned repos"""
        base_dir = self.config.get('base_dir')
        return Path(base_dir).expanduser().resolve() if base_dir else None
    

    def set_base_dir(self, path: Path) -> None:
        self.config['base_dir'] = str(path.expanduser().resolve())
        self.save_config


    def get_preffered_editor(self, editor: str) -> None:
        return self.config.get('preferred_editor')
    

    def set_preferred_editor(self, editor: str) -> None:
        if editor not in SUPPORTED_EDITORS:
            raise ValueError(f"Unsupported editor: {editor}")
        self.config['preferred_editor'] = editor
        self.save_cache()


    def get_auto_open_editor(self) -> bool:
        return self.config.get('auto_open_editor', False)
    

    def set_auto_open_editor(self, auto_open: bool) -> None:
        self.config['auto_open_editor'] = auto_open
        self.save_config()


    def get_default_organization(self) -> str:
        return self.config.get('organization_method', 'platform')
    
    def set_default_organization(self, method: str) -> None:
        valid_methods = ['platform', 'owner', 'flat']
        if method not in valid_methods:
            raise ValueError("unsuported methods")
        self.config['organization_method'] = method
        self.save_config()


    def cache_recent_repo(self, repo_info: Dict[str, str], path: str) -> None:
        if 'recent_repos' not in self.cache:
            self.cache['recent_repos'] = []

        repo_data = {
            'name': repo_info['full_name'],
            'path': path,
            'platform': repo_info['platform'],
            'clone_at': self._get_current_timestamp()
        }

        # remove if already exists
        self.cache['recent_repos'] = [
            r for r in self.cache['recent_repos']
            if r['name'] != repo_info['full_name']
        ]

        self.cache['recent_repos'].insert(0, repo_data)
        self.cache['recent_repos'] = self.cache['recent_repos'][:10]

        self.save_cache()


    
    def get_recent_repos(self, limit: int =5) -> List[Dict[str, Any]]:
        return self.cache.get('recent_repos', [])[:limit]
    

    def cache_editor_choice(self, editor: str) -> None:
        self.cache['last_editor_choice'] = editor
        self.save_cache()


    def get_cached_editor_choice(self) -> Optional[str]:
        """Get the last editor choice from cache"""
        return self.cache.get('last_editor_choice')
    
    def is_configured(self) -> bool:
        """Check if basic configuration is complete"""
        return (
            self.get_base_dir() is not None and
            self.get_base_dir().exists()
        )
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration for display"""
        return self.config.copy()
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def reset_config(self) -> None:
        """Reset configuration to defaults"""
        self.config = DEFAULT_CONFIG.copy()
        self.save_config()
        
        # Also clear cache
        self.cache = {}
        self.save_cache()