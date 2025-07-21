"""Open command implementation."""

import click
import subprocess
from pathlib import Path
from .base import BaseCommand
from ..ui.display import print_info, print_success, print_error, print_warning


@click.command()
@click.argument('repository', required=False)
@click.option('--editor', '-e', help='Specify editor to use')
@click.option('--list', '-l', 'list_repos', is_flag=True, help='List available repositories')
def command(repository, editor, list_repos):
    """Open a repository in your preferred editor."""
    base_cmd = BaseCommand()
    config = base_cmd.config
    
    if list_repos:
        list_available_repositories(config)
        return
    
    if not repository:
        repository = prompt_for_repository(config)
        if not repository:
            return
    
    # Find repository path
    repo_path = find_repository_path(config, repository)
    if not repo_path:
        print_error(f"Repository '{repository}' not found")
        suggest_similar_repositories(config, repository)
        return
    
    # Determine editor to use
    editor_to_use = editor or config.config.get('preferred_editor')
    if not editor_to_use:
        editor_to_use = prompt_for_editor(config)
        if not editor_to_use:
            print_error("No editor specified")
            return
    
    # Open in editor
    if open_in_editor(config, repo_path, editor_to_use):
        print_success(f"🚀 Opened {repository} in {editor_to_use}")
    else:
        print_error(f"Failed to open {repository} in {editor_to_use}")


def list_available_repositories(config):
    """List all available repositories."""
    cache = config.cache
    repositories = cache.get('repositories', [])
    
    if not repositories:
        print_warning("No repositories found. Use 'shelly clone <url>' to add some!")
        return
    
    print_info("📁 Available repositories:")
    
    # Group by category
    categories = {}
    for repo in repositories:
        cat = repo.get('category', 'uncategorized')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(repo)
    
    for cat, repos in sorted(categories.items()):
        click.echo(f"\n📂 {cat.upper()}:")
        for repo in repos:
            name = repo.get('name', 'Unknown')
            owner = repo.get('owner', '')
            display_name = f"{owner}/{name}" if owner else name
            click.echo(f"  • {name} ({display_name})")


def prompt_for_repository(config):
    """Prompt user to select a repository."""
    cache = config.cache
    repositories = cache.get('repositories', [])
    
    if not repositories:
        print_warning("No repositories found. Use 'shelly clone <url>' to add some!")
        return None
    
    print_info("Available repositories:")
    repo_names = []
    for i, repo in enumerate(repositories, 1):
        name = repo.get('name', 'Unknown')
        owner = repo.get('owner', '')
        category = repo.get('category', 'uncategorized')
        display_name = f"{owner}/{name}" if owner else name
        
        click.echo(f"  {i}. {name} ({display_name}) [{category}]")
        repo_names.append(name)
    
    while True:
        choice = click.prompt("Select repository (number or name)", type=str)
        
        # Check if it's a number
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(repositories):
                return repositories[choice_num - 1]['name']
            else:
                print_error("Invalid choice")
                continue
        except ValueError:
            # Not a number, check if it's a valid repository name
            if choice in repo_names:
                return choice
            else:
                print_error(f"Repository '{choice}' not found")
                continue


def find_repository_path(config, repository_name):
    """Find the path to a repository by name."""
    cache = config.cache
    repositories = cache.get('repositories', [])
    
    for repo in repositories:
        if repo.get('name') == repository_name:
            path = Path(repo.get('path', ''))
            if path.exists():
                return path
            else:
                print_warning(f"Repository path {path} no longer exists")
                return None
    
    return None


def suggest_similar_repositories(config, repository_name):
    """Suggest similar repository names."""
    cache = config.cache
    repositories = cache.get('repositories', [])
    
    # Simple fuzzy matching
    similar = []
    for repo in repositories:
        name = repo.get('name', '')
        if repository_name.lower() in name.lower() or name.lower() in repository_name.lower():
            similar.append(name)
    
    if similar:
        print_info("Did you mean one of these?")
        for name in similar[:5]:  # Show max 5 suggestions
            click.echo(f"  • {name}")


def prompt_for_editor(config):
    """Prompt user to select an editor."""
    editors = config.config.get('supported_editors', {})
    available = []
    
    # Check which editors are available
    import shutil
    for editor_name, editor_config in editors.items():
        if shutil.which(editor_config['command']):
            available.append(editor_name)
    
    if not available:
        print_error("No supported editors found")
        return None
    
    if len(available) == 1:
        return available[0]
    
    print_info("Available editors:")
    for i, editor in enumerate(available, 1):
        click.echo(f"  {i}. {editor}")
    
    choice = click.prompt("Select editor", type=click.IntRange(1, len(available)))
    return available[choice - 1]


def open_in_editor(config, repo_path, editor_name):
    """Open repository in the specified editor."""
    editors = config.config.get('supported_editors', {})
    
    if editor_name not in editors:
        print_error(f"Unknown editor: {editor_name}")
        return False
    
    editor_config = editors[editor_name]
    command = [editor_config['command']] + editor_config.get('args', [])
    
    try:
        subprocess.Popen(command, cwd=str(repo_path))
        return True
    except Exception as e:
        print_error(f"Failed to open editor: {e}")
        return False


# Alias for import
open_cmd = command
