"""Repository management functionality."""

import os
import subprocess
from .utils import get_repo_path, validate_url

class Repository:
    def __init__(self, url):
        self.url = url
        self.name = url.split('/')[-1].replace('.git', '')

    def clone(self, path=None):
        """Clone the repository."""
        target_path = path or get_repo_path(self.name)
        if os.path.exists(target_path):
            raise ValueError(f"Path already exists: {target_path}")
        
        subprocess.run(['git', 'clone', self.url, target_path], check=True)

    @staticmethod
    def list_all():
        """List all managed repositories."""
        # Implementation depends on how repositories are tracked
        pass
