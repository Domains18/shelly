"""
Status command implementation
Shows git status for all repositories with visual indicators
"""

import click
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base import BaseCommand
from ..ui.display import print_success, print_error, print_info, print_warning


@click.command()
@click.option('--category', '-c', help='Filter by category')
@click.option('--dirty-only', '-d', is_flag=True, help='Show only repositories with changes')
@click.option('--detailed', is_flag=True, help='Show detailed git status for each repo')
@click.option('--fetch', '-f', is_flag=True, help='Fetch from remotes before checking status')
def command(category, dirty_only, detailed, fetch):
    """Show git status for all managed repositories."""
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
    
    print_info(f"🔍 Checking status of {len(repositories)} repositories...")
    if fetch:
        print_info("📡 Fetching from remotes (this may take a moment)...")
    
    # Check status of all repositories in parallel
    repo_statuses = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_repo = {
            executor.submit(get_repository_status, repo, fetch): repo 
            for repo in repositories
        }
        
        for future in as_completed(future_to_repo):
            repo = future_to_repo[future]
            try:
                status = future.result()
                if status:
                    repo_statuses.append(status)
            except Exception as e:
                print_error(f"Error checking {repo.get('name', 'unknown')}: {e}")
    
    # Filter to dirty repos only if requested
    if dirty_only:
        repo_statuses = [status for status in repo_statuses if status['has_changes']]
    
    if not repo_statuses:
        if dirty_only:
            print_success("✨ All repositories are clean!")
        else:
            print_warning("No repository status information available")
        return
    
    # Display results
    display_status_summary(repo_statuses, detailed)


def get_repository_status(repo_info, fetch=False):
    """Get git status for a single repository."""
    repo_path = Path(repo_info.get('path', ''))
    
    if not repo_path.exists():
        return {
            'name': repo_info.get('name', 'Unknown'),
            'category': repo_info.get('category', 'uncategorized'),
            'path': str(repo_path),
            'error': 'Repository path not found',
            'has_changes': False
        }
    
    if not (repo_path / '.git').exists():
        return {
            'name': repo_info.get('name', 'Unknown'),
            'category': repo_info.get('category', 'uncategorized'),
            'path': str(repo_path),
            'error': 'Not a git repository',
            'has_changes': False
        }
    
    try:
        # Change to repository directory
        original_cwd = Path.cwd()
        
        status_info = {
            'name': repo_info.get('name', 'Unknown'),
            'category': repo_info.get('category', 'uncategorized'),
            'path': str(repo_path),
            'has_changes': False,
            'branch': None,
            'ahead': 0,
            'behind': 0,
            'staged': [],
            'modified': [],
            'untracked': [],
            'conflicts': [],
            'stashes': 0,
            'error': None
        }
        
        # Fetch if requested
        if fetch:
            try:
                subprocess.run(['git', 'fetch', '--all'], 
                             cwd=repo_path, 
                             capture_output=True, 
                             timeout=30)
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                pass  # Continue even if fetch fails
        
        # Get current branch
        result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                               cwd=repo_path, capture_output=True, text=True)
        if result.returncode == 0:
            status_info['branch'] = result.stdout.strip()
        
        # Get ahead/behind count
        if status_info['branch'] and status_info['branch'] != 'HEAD':
            try:
                result = subprocess.run([
                    'git', 'rev-list', '--left-right', '--count', 
                    f"{status_info['branch']}...origin/{status_info['branch']}"
                ], cwd=repo_path, capture_output=True, text=True)
                
                if result.returncode == 0:
                    ahead, behind = result.stdout.strip().split('\t')
                    status_info['ahead'] = int(ahead)
                    status_info['behind'] = int(behind)
            except (ValueError, subprocess.CalledProcessError):
                pass
        
        # Get git status --porcelain
        result = subprocess.run(['git', 'status', '--porcelain'], 
                               cwd=repo_path, capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if not line:
                    continue
                    
                status_code = line[:2]
                filename = line[3:]
                
                if status_code.startswith('U') or status_code.endswith('U') or status_code == 'DD':
                    status_info['conflicts'].append(filename)
                elif status_code[0] in 'MADRC':
                    status_info['staged'].append(filename)
                elif status_code[1] in 'MD':
                    status_info['modified'].append(filename)
                elif status_code.startswith('??'):
                    status_info['untracked'].append(filename)
        
        # Check for stashes
        result = subprocess.run(['git', 'stash', 'list'], 
                               cwd=repo_path, capture_output=True, text=True)
        if result.returncode == 0:
            status_info['stashes'] = len([line for line in result.stdout.strip().split('\n') if line])
        
        # Determine if repository has changes
        status_info['has_changes'] = (
            bool(status_info['staged']) or 
            bool(status_info['modified']) or 
            bool(status_info['untracked']) or 
            bool(status_info['conflicts']) or
            status_info['ahead'] > 0 or
            status_info['behind'] > 0
        )
        
        return status_info
        
    except Exception as e:
        return {
            'name': repo_info.get('name', 'Unknown'),
            'category': repo_info.get('category', 'uncategorized'),
            'path': str(repo_path),
            'error': str(e),
            'has_changes': False
        }


def display_status_summary(repo_statuses, detailed=False):
    """Display repository status summary."""
    from rich.console import Console
    from rich.table import Table
    from rich.text import Text
    
    console = Console()
    
    # Group by category
    categories = {}
    for status in repo_statuses:
        cat = status.get('category', 'uncategorized')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(status)
    
    total_repos = len(repo_statuses)
    dirty_repos = len([s for s in repo_statuses if s['has_changes']])
    clean_repos = total_repos - dirty_repos
    
    # Summary header
    console.print(f"\n📊 Repository Status Summary", style="cyan bold")
    console.print(f"Total: {total_repos} | Clean: {clean_repos} | With Changes: {dirty_repos}")
    
    for category_name, repos in sorted(categories.items()):
        console.print(f"\n📁 {category_name.upper()}", style="blue bold")
        
        if detailed:
            # Detailed table
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Repository", style="cyan")
            table.add_column("Branch", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Changes", style="red")
            
            for repo in repos:
                name = repo['name']
                branch = repo.get('branch', 'unknown')
                
                # Status indicators
                status_parts = []
                if repo.get('error'):
                    status_parts.append(f"❌ {repo['error']}")
                else:
                    if repo['ahead'] > 0:
                        status_parts.append(f"↑{repo['ahead']}")
                    if repo['behind'] > 0:
                        status_parts.append(f"↓{repo['behind']}")
                    if not status_parts:
                        status_parts.append("✓")
                
                # Changes summary
                changes_parts = []
                if repo.get('conflicts'):
                    changes_parts.append(f"🔥{len(repo['conflicts'])}")
                if repo.get('staged'):
                    changes_parts.append(f"📦{len(repo['staged'])}")
                if repo.get('modified'):
                    changes_parts.append(f"📝{len(repo['modified'])}")
                if repo.get('untracked'):
                    changes_parts.append(f"❓{len(repo['untracked'])}")
                if repo.get('stashes', 0) > 0:
                    changes_parts.append(f"📚{repo['stashes']}")
                
                table.add_row(
                    name,
                    branch,
                    " ".join(status_parts),
                    " ".join(changes_parts) if changes_parts else "clean"
                )
            
            console.print(table)
        else:
            # Simple list
            for repo in repos:
                status_icon = get_status_icon(repo)
                name = repo['name']
                branch = repo.get('branch', 'unknown')
                
                console.print(f"  {status_icon} {name} [{branch}]")
    
    # Legend
    if detailed:
        console.print("\n📖 Legend:", style="dim")
        console.print("  ↑n ahead  ↓n behind  🔥 conflicts  📦 staged  📝 modified  ❓ untracked  📚 stashes", style="dim")


def get_status_icon(repo_status):
    """Get appropriate status icon for repository."""
    if repo_status.get('error'):
        return '❌'
    elif repo_status.get('conflicts'):
        return '🔥'
    elif repo_status['ahead'] > 0 or repo_status['behind'] > 0:
        return '🔄'
    elif repo_status.get('staged') or repo_status.get('modified'):
        return '📝'
    elif repo_status.get('untracked'):
        return '❓'
    else:
        return '✅'


# Alias for import
status = command
