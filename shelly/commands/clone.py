"""
Clone command implementation
Handles cloning repositories with category organization
"""

import click
import os
import re
from pathlib import Path
from urllib.parse import urlparse

from .base import BaseCommand
from ..ui.display import print_success, print_error, print_info, print_warning


@click.command()
@click.argument('url', required=True)
@click.option('--category', '-c', help='Category to organize the repository under')
@click.option('--path', '-p', help='Custom path to clone the repository')
@click.option('--shallow', is_flag=True, help='Perform a shallow clone')
@click.option('--no-open', is_flag=True, help='Don\'t open in editor after cloning')
def command(url, category, path, shallow, no_open):
    """Clone a Git repository and organize it by category"""
    
    # Initialize base command for config access
    base_cmd = BaseCommand()
    config = base_cmd.config
    
    try:
        # Parse repository information from URL
        repo_info = parse_git_url(url)
        if not repo_info:
            print_error("Invalid repository URL")
            return 1
            
        print_info(f"📦 Repository: {repo_info['name']} ({repo_info['platform']})")
        
        # Determine category
        if not category:
            category = prompt_for_category(config)
        
        # Determine destination path
        if path:
            destination = Path(path).expanduser().resolve()
        else:
            base_dir = Path(config.config.get('base_dir', '~/Code')).expanduser()
            destination = base_dir / category / repo_info['name']
        
        # Create destination directory
        destination.mkdir(parents=True, exist_ok=True)
        
        # Check if destination already exists and has content
        if destination.exists() and any(destination.iterdir()):
            if not click.confirm(f"Directory {destination} already exists and is not empty. Continue?"):
                print_info("Cancelled")
                return 0
        
        # Build git clone command
        clone_cmd = ['git', 'clone']
        if shallow:
            clone_cmd.extend(['--depth', '1'])
        clone_cmd.extend([url, str(destination)])
        
        # Clone the repository
        print_info(f"🚀 Cloning to: {destination}")
        
        import subprocess
        result = subprocess.run(clone_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print_error(f"Failed to clone repository: {result.stderr}")
            return 1
        
        print_success(f"✅ Successfully cloned {repo_info['name']} to {destination}")
        
        # Add category to config if it's new
        categories = config.config.get('categories', [])
        if category not in categories:
            categories.append(category)
            config.config['categories'] = sorted(categories)
            config.save_config()
        
        # Cache the cloned repository
        cache_repository(config, repo_info, str(destination), category)
        
        # Open in editor if requested
        if not no_open:
            open_in_editor(config, destination)
        
        return 0
        
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        return 1


def parse_git_url(url):
    """Parse a Git URL and extract repository information"""
    # Support various Git URL formats
    patterns = [
        r'https://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$',
        r'git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$',
        r'https://gitlab\.com/([^/]+)/([^/]+?)(?:\.git)?/?$',
        r'git@gitlab\.com:([^/]+)/([^/]+?)(?:\.git)?$',
        r'https://bitbucket\.org/([^/]+)/([^/]+?)(?:\.git)?/?$',
        r'git@bitbucket\.org:([^/]+)/([^/]+?)(?:\.git)?$',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            owner, name = match.groups()
            
            # Determine platform
            if 'github.com' in url:
                platform = 'github'
            elif 'gitlab.com' in url:
                platform = 'gitlab'
            elif 'bitbucket.org' in url:
                platform = 'bitbucket'
            else:
                platform = 'unknown'
            
            return {
                'owner': owner,
                'name': name,
                'platform': platform,
                'full_name': f"{owner}/{name}",
                'url': url
            }
    
    return None


def prompt_for_category(config):
    """Prompt user to select or create a category"""
    categories = config.config.get('categories', [
        'work', 'personal', 'learning', 'opensource', 'misc'
    ])
    
    print_info("Available categories:")
    for i, cat in enumerate(categories, 1):
        click.echo(f"  {i}. {cat}")
    
    click.echo(f"  {len(categories) + 1}. Create new category")
    
    while True:
        choice = click.prompt("Select category (number or name)", type=str)
        
        # Check if it's a number
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(categories):
                return categories[choice_num - 1]
            elif choice_num == len(categories) + 1:
                new_category = click.prompt("Enter new category name").strip().lower()
                if new_category:
                    return new_category
            else:
                print_error("Invalid choice")
                continue
        except ValueError:
            # Not a number, check if it's a valid category name
            choice = choice.strip().lower()
            if choice in categories:
                return choice
            else:
                # Create new category
                if click.confirm(f"Create new category '{choice}'?"):
                    return choice
                continue


def cache_repository(config, repo_info, path, category):
    """Cache repository information for quick access"""
    cache = config.cache
    
    if 'repositories' not in cache:
        cache['repositories'] = []
    
    # Remove existing entry if it exists
    cache['repositories'] = [
        repo for repo in cache['repositories'] 
        if repo.get('path') != path
    ]
    
    # Add new entry
    cache['repositories'].append({
        'name': repo_info['name'],
        'owner': repo_info['owner'],
        'platform': repo_info['platform'],
        'url': repo_info['url'],
        'path': path,
        'category': category,
        'cloned_at': str(__import__('datetime').datetime.now())
    })
    
    config.save_cache()


def open_in_editor(config, path):
    """Open repository in configured editor"""
    editor = config.config.get('preferred_editor')
    
    if not editor and click.confirm("Would you like to open the repository in an editor?"):
        # Try to detect available editors
        editors = config.config.get('supported_editors', {})
        available = []
        
        for editor_name, editor_config in editors.items():
            import shutil
            if shutil.which(editor_config['command']):
                available.append(editor_name)
        
        if available:
            if len(available) == 1:
                editor = available[0]
            else:
                print_info("Available editors:")
                for i, ed in enumerate(available, 1):
                    click.echo(f"  {i}. {ed}")
                
                choice = click.prompt("Select editor (number)", type=int)
                if 1 <= choice <= len(available):
                    editor = available[choice - 1]
    
    if editor:
        editors = config.config.get('supported_editors', {})
        if editor in editors:
            editor_config = editors[editor]
            command = [editor_config['command']] + editor_config.get('args', [])
            
            try:
                import subprocess
                subprocess.Popen(command, cwd=str(path))
                print_success(f"🚀 Opened in {editor}")
            except Exception as e:
                print_error(f"Failed to open editor: {e}")


# Alias for compatibility
clone = command