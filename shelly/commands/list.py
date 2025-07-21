"""List command implementation."""

import click
from pathlib import Path
from .base import BaseCommand
from ..ui.display import print_info, print_success, print_warning


@click.command()
@click.option('--category', '-c', help='Filter by category')
@click.option('--recent', '-r', is_flag=True, help='Show recently cloned repositories')
@click.option('--path', '-p', is_flag=True, help='Show full paths')
def command(category, recent, path):
    """List managed repositories."""
    base_cmd = BaseCommand()
    config = base_cmd.config
    
    cache = config.cache
    repositories = cache.get('repositories', [])
    
    if not repositories:
        print_warning("No repositories found. Use 'shelly clone <url>' to add some!")
        return
    
    # Filter by category if specified
    if category:
        repositories = [repo for repo in repositories if repo.get('category') == category]
        if not repositories:
            print_warning(f"No repositories found in category '{category}'")
            return
    
    # Sort by most recent if requested
    if recent:
        repositories = sorted(repositories, key=lambda x: x.get('cloned_at', ''), reverse=True)[:10]
    
    # Group by category
    categories = {}
    for repo in repositories:
        cat = repo.get('category', 'uncategorized')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(repo)
    
    # Display repositories
    total_count = 0
    for cat, repos in sorted(categories.items()):
        print_success(f"\n📁 {cat.upper()} ({len(repos)} repositories)")
        
        for repo in repos:
            name = repo.get('name', 'Unknown')
            owner = repo.get('owner', '')
            platform = repo.get('platform', '')
            repo_path = repo.get('path', '')
            
            # Create display string
            display_name = f"{owner}/{name}" if owner else name
            platform_emoji = {
                'github': '🐙',
                'gitlab': '🦊', 
                'bitbucket': '📘'
            }.get(platform, '📦')
            
            if path:
                click.echo(f"  {platform_emoji} {display_name}")
                click.echo(f"    📂 {repo_path}")
            else:
                click.echo(f"  {platform_emoji} {display_name}")
            
            total_count += 1
    
    if not category:
        print_info(f"\n✨ Total: {total_count} repositories")
        
        # Show available categories
        all_categories = list(categories.keys())
        if len(all_categories) > 1:
            print_info(f"📋 Categories: {', '.join(all_categories)}")


# Alias for import
list_cmd = command
