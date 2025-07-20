"""Editor integration functionality."""

import subprocess
from .utils import get_repo_path

class Editor:
    def __init__(self, editor_command):
        self.editor_command = editor_command

    def open(self, repository):
        """Open repository in configured editor."""
        path = get_repo_path(repository)
        subprocess.run([self.editor_command, path], check=True)
