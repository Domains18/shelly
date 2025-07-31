# shelly/commands/clone.py
"""Clone command implementation with support for shorthand and multiple clone methods."""

import click
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from .base import BaseCommand
from ..ui.display import print_success, print_error, print_info, print_warning
from .clone_utils import parse_git_url, get_destination_path # (We'll move helpers to a new file)

@click.command()
@click.argument('repository')
@click.option('--method', '-m', type=click.Choice(['httpss', 'ssh', 'gh'], case_sensitive=False), help='Override the default clone method.')
@click.option('--category', '-c', help='Category to organize the repository under.')
@click.option('--path', '-p', help='Custom absolute path to clone into.')
@click.option('--shallow', is_flag=True, help='Perform a shallow clone (--depth 1).')
def command(repository: str, method: Optional[str], category: Optional[str], path: Optional[str], shallow: bool):
    """
    Clone a Git repository from a URL or shorthand (e.g., 'owner/repo').
    
    Examples:
      shelly clone torvalds/linux
      shelly clone torvalds/linux --method ssh
      shelly clone https://gitlab.com/gitlab-org/gitlab
    """
    if not shutil.which("git"):
        print_error("Git is not installed or not in your PATH. Please install Git.")
        return 1

    base_cmd = BaseCommand()
    config = base_cmd.config
    
    # 1. Determine clone method (command-line option > config > default)
    clone_method = method or config.config.get('clone_protocol', 'httpss')
    
    # 2. Resolve repository shorthand (e.g., "owner/repo") into a full URL
    repo_info = _resolve_repository(repository, config)
    if not repo_info:
        return 1 # Error already printed
        
    # 3. Determine destination path
    dest_path = get_destination_path(repo_info, config, category, path)
    dest_path.mkdir(parents=True, exist_ok=True)
    if any(dest_path.iterdir()):
        if not click.confirm(f"⚠️ Directory '{dest_path}' is not empty. Continue?"):
            print_info("Clone cancelled.")
            return 0
    
    print_info(f"📦 Repository: {repo_info['full_name']} ({repo_info['platform']})")
    print_info(f"🚀 Cloning with '{clone_method.upper()}' into: {dest_path}")

    # 4. Dispatch to the correct clone function
    success = False
    if clone_method == 'gh':
        success = _clone_with_gh(repo_info['full_name'], str(dest_path))
    else: # https or ssh
        clone_url = f"git@{repo_info['host']}:{repo_info['full_name']}.git" if clone_method == 'ssh' else repo_info['https_url']
        success = _clone_with_git(clone_url, str(dest_path), shallow)

    if not success:
        print_error("Clone failed. Please check the error message above.")
        return 1
        
    print_success(f"✅ Successfully cloned {repo_info['name']}")
    # Add to cache, open in editor etc.
    # (Your existing caching and open_in_editor logic can be called here)

def _resolve_repository(repo_string: str, config) -> Optional[dict]:
    """Resolve a shorthand or URL into a structured repository dictionary."""
    # If it looks like a URL, parse it directly
    if repo_string.startswith(('http', 'git@')):
        return parse_git_url(repo_string)

    # Otherwise, treat as shorthand "owner/repo"
    if '/' not in repo_string:
        print_error(f"Invalid shorthand '{repo_string}'. Must be in 'owner/repo' format.")
        return None
        
    default_platform = config.config.get('default_platform', 'github')
    # Construct a full URL to pass to the robust parser
    # This avoids duplicating logic
    if default_platform == 'github':
        full_url = f"https://github.com/{repo_string}"
    elif default_platform == 'gitlab':
        full_url = f"https://gitlab.com/{repo_string}"
    elif default_platform == 'bitbucket':
        full_url = f"https://bitbucket.org/{repo_string}"
    else:
        print_error(f"Unsupported default platform '{default_platform}' in config.")
        return None
        
    print_info(f"Resolved shorthand '{repo_string}' using default platform '{default_platform}'.")
    return parse_git_url(full_url)

def _clone_with_git(url: str, dest: str, shallow: bool) -> bool:
    """Clones using the standard git command."""
    cmd = ['git', 'clone']
    if shallow:
        cmd.extend(['--depth', '1'])
    cmd.extend([url, dest])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print_error(f"Git Error: {result.stderr.strip()}")
        return False
    return True

def _clone_with_gh(repo_name: str, dest: str) -> bool:
    """Clones using the 'gh' command-line tool."""
    if not shutil.which('gh'):
        print_error("Cannot clone: 'gh' command not found. Please install the GitHub CLI.")
        return False
        
    cmd = ['gh', 'repo', 'clone', repo_name, dest]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print_error(f"GitHub CLI Error: {result.stderr.strip()}")
        return False
    return True

clone = command