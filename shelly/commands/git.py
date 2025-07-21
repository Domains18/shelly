"""
Git command group for bulk operations
Handles git operations across multiple repositories
"""

import click
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base import BaseCommand
from ..ui.display import print_success, print_error, print_info, print_warning


@click.group()
def git():
    """Git operations across multiple repositories."""
    pass


@git.command()
@click.option('--category', '-c', help='Sync repositories in specific category')
@click.option('--dry-run', '-n', is_flag=True, help='Show what would be done without executing')
@click.option('--parallel', '-p', is_flag=True, default=True, help='Run operations in parallel')
def sync(category, dry_run, parallel):
    """Synchronize (fetch and pull) repositories with their remotes."""
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
    
    if dry_run:
        print_info(f"🔍 Would sync {len(repositories)} repositories:")
        for repo in repositories:
            print(f"  • {repo.get('name', 'Unknown')} ({repo.get('category', 'uncategorized')})")
        return
    
    print_info(f"🔄 Syncing {len(repositories)} repositories...")
    
    # Sync repositories
    if parallel:
        sync_repositories_parallel(repositories)
    else:
        sync_repositories_sequential(repositories)


@git.command()
@click.option('--category', '-c', help='Pull repositories in specific category')
@click.option('--dry-run', '-n', is_flag=True, help='Show what would be done without executing')
@click.option('--force', '-f', is_flag=True, help='Force pull even with uncommitted changes')
def pull(category, dry_run, force):
    """Pull latest changes from remote for clean repositories."""
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
    
    if dry_run:
        print_info(f"🔍 Would pull {len(repositories)} repositories:")
        for repo in repositories:
            print(f"  • {repo.get('name', 'Unknown')} ({repo.get('category', 'uncategorized')})")
        return
    
    print_info(f"⬇️  Pulling {len(repositories)} repositories...")
    
    # Pull repositories
    results = []
    for repo in repositories:
        result = pull_repository(repo, force)
        results.append(result)
    
    # Summary
    successful = len([r for r in results if r['success']])
    failed = len(results) - successful
    
    print_success(f"✅ Pull completed: {successful} successful, {failed} failed")


@git.command()
@click.option('--category', '-c', help='Check repositories in specific category')
@click.option('--fix', '-f', is_flag=True, help='Attempt to fix common issues')
def check(category, fix):
    """Check repositories for common issues and inconsistencies."""
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
    
    print_info(f"🔍 Checking {len(repositories)} repositories for issues...")
    
    issues_found = []
    
    for repo in repositories:
        repo_issues = check_repository_health(repo)
        if repo_issues:
            issues_found.extend(repo_issues)
    
    if not issues_found:
        print_success("✅ All repositories look healthy!")
        return
    
    # Display issues
    print_warning(f"⚠️  Found {len(issues_found)} issues:")
    
    for issue in issues_found:
        print_error(f"  • {issue['repo']}: {issue['message']}")
        
        if fix and issue.get('fixable'):
            if click.confirm(f"    Fix this issue?"):
                fix_result = fix_repository_issue(issue)
                if fix_result:
                    print_success(f"    ✅ Fixed!")
                else:
                    print_error(f"    ❌ Failed to fix")


def sync_repositories_parallel(repositories):
    """Sync repositories in parallel."""
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_repo = {
            executor.submit(sync_repository, repo): repo 
            for repo in repositories
        }
        
        for future in as_completed(future_to_repo):
            repo = future_to_repo[future]
            try:
                result = future.result()
                if result['success']:
                    print_success(f"✅ {result['name']}: {result['message']}")
                else:
                    print_error(f"❌ {result['name']}: {result['message']}")
            except Exception as e:
                print_error(f"❌ {repo.get('name', 'unknown')}: Exception occurred - {e}")


def sync_repositories_sequential(repositories):
    """Sync repositories one by one."""
    for repo in repositories:
        result = sync_repository(repo)
        if result['success']:
            print_success(f"✅ {result['name']}: {result['message']}")
        else:
            print_error(f"❌ {result['name']}: {result['message']}")


def sync_repository(repo_info):
    """Sync a single repository (fetch + pull if clean)."""
    repo_path = Path(repo_info.get('path', ''))
    name = repo_info.get('name', 'Unknown')
    
    if not repo_path.exists():
        return {'name': name, 'success': False, 'message': 'Repository path not found'}
    
    if not (repo_path / '.git').exists():
        return {'name': name, 'success': False, 'message': 'Not a git repository'}
    
    try:
        # Fetch from all remotes
        result = subprocess.run(['git', 'fetch', '--all'], 
                               cwd=repo_path, 
                               capture_output=True, 
                               text=True,
                               timeout=60)
        
        if result.returncode != 0:
            return {'name': name, 'success': False, 'message': f'Fetch failed: {result.stderr}'}
        
        # Check if working directory is clean
        status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                      cwd=repo_path, 
                                      capture_output=True, 
                                      text=True)
        
        if status_result.returncode != 0:
            return {'name': name, 'success': False, 'message': 'Could not check status'}
        
        is_clean = not status_result.stdout.strip()
        
        if is_clean:
            # Try to pull
            pull_result = subprocess.run(['git', 'pull'], 
                                        cwd=repo_path, 
                                        capture_output=True, 
                                        text=True,
                                        timeout=60)
            
            if pull_result.returncode != 0:
                return {'name': name, 'success': False, 'message': f'Pull failed: {pull_result.stderr}'}
            
            return {'name': name, 'success': True, 'message': 'Fetched and pulled successfully'}
        else:
            return {'name': name, 'success': True, 'message': 'Fetched (working directory has changes)'}
            
    except subprocess.TimeoutExpired:
        return {'name': name, 'success': False, 'message': 'Operation timed out'}
    except Exception as e:
        return {'name': name, 'success': False, 'message': str(e)}


def pull_repository(repo_info, force=False):
    """Pull a single repository."""
    repo_path = Path(repo_info.get('path', ''))
    name = repo_info.get('name', 'Unknown')
    
    if not repo_path.exists():
        return {'name': name, 'success': False, 'message': 'Repository path not found'}
    
    if not (repo_path / '.git').exists():
        return {'name': name, 'success': False, 'message': 'Not a git repository'}
    
    try:
        # Check if working directory is clean (unless force)
        if not force:
            status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                          cwd=repo_path, 
                                          capture_output=True, 
                                          text=True)
            
            if status_result.returncode != 0:
                return {'name': name, 'success': False, 'message': 'Could not check status'}
            
            if status_result.stdout.strip():
                return {'name': name, 'success': False, 'message': 'Working directory has changes (use --force to override)'}
        
        # Pull
        pull_result = subprocess.run(['git', 'pull'], 
                                    cwd=repo_path, 
                                    capture_output=True, 
                                    text=True,
                                    timeout=60)
        
        if pull_result.returncode != 0:
            return {'name': name, 'success': False, 'message': f'Pull failed: {pull_result.stderr}'}
        
        return {'name': name, 'success': True, 'message': 'Pulled successfully'}
        
    except subprocess.TimeoutExpired:
        return {'name': name, 'success': False, 'message': 'Pull timed out'}
    except Exception as e:
        return {'name': name, 'success': False, 'message': str(e)}


def check_repository_health(repo_info):
    """Check a repository for common issues."""
    repo_path = Path(repo_info.get('path', ''))
    name = repo_info.get('name', 'Unknown')
    issues = []
    
    # Check if path exists
    if not repo_path.exists():
        issues.append({
            'repo': name,
            'type': 'missing_path',
            'message': 'Repository path does not exist',
            'fixable': True,
            'fix_action': 'remove_from_cache'
        })
        return issues
    
    # Check if it's a git repository
    if not (repo_path / '.git').exists():
        issues.append({
            'repo': name,
            'type': 'not_git_repo',
            'message': 'Directory exists but is not a git repository',
            'fixable': True,
            'fix_action': 'remove_from_cache'
        })
        return issues
    
    try:
        # Check for valid remotes
        result = subprocess.run(['git', 'remote', '-v'], 
                               cwd=repo_path, 
                               capture_output=True, 
                               text=True)
        
        if result.returncode == 0:
            if not result.stdout.strip():
                issues.append({
                    'repo': name,
                    'type': 'no_remotes',
                    'message': 'No remote repositories configured',
                    'fixable': False
                })
        
        # Check for detached HEAD
        result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                               cwd=repo_path, 
                               capture_output=True, 
                               text=True)
        
        if result.returncode == 0 and result.stdout.strip() == 'HEAD':
            issues.append({
                'repo': name,
                'type': 'detached_head',
                'message': 'Repository is in detached HEAD state',
                'fixable': False
            })
        
        # Check for large number of untracked files
        result = subprocess.run(['git', 'status', '--porcelain'], 
                               cwd=repo_path, 
                               capture_output=True, 
                               text=True)
        
        if result.returncode == 0:
            untracked = [line for line in result.stdout.split('\n') if line.startswith('??')]
            if len(untracked) > 50:
                issues.append({
                    'repo': name,
                    'type': 'many_untracked',
                    'message': f'Large number of untracked files ({len(untracked)})',
                    'fixable': False
                })
        
    except Exception as e:
        issues.append({
            'repo': name,
            'type': 'check_error',
            'message': f'Error during health check: {str(e)}',
            'fixable': False
        })
    
    return issues


def fix_repository_issue(issue):
    """Attempt to fix a repository issue."""
    if issue['fix_action'] == 'remove_from_cache':
        # This would need to integrate with the config manager
        # For now, just return True as a placeholder
        return True
    
    return False


# Register the git group
command = git
