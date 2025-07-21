"""
Git integration utilities for Shelly CLI
Advanced git operations and repository management
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from git import Repo, InvalidGitRepositoryError
from ..ui.display import print_info, print_success, print_error, print_warning


class GitManager:
    """Advanced Git operations manager"""
    
    @staticmethod
    def get_repo_info(repo_path: Path) -> Optional[Dict]:
        """Get comprehensive repository information"""
        try:
            repo = Repo(repo_path)
            
            # Get remote information
            remotes = {}
            for remote in repo.remotes:
                remotes[remote.name] = {
                    'url': list(remote.urls)[0] if remote.urls else None,
                    'fetch_url': remote.url,
                    'push_url': getattr(remote, 'pushurl', remote.url)
                }
            
            # Get branch information
            branches = {
                'current': repo.active_branch.name if repo.active_branch else None,
                'local': [branch.name for branch in repo.branches],
                'remote': [ref.name for ref in repo.remote().refs] if repo.remotes else []
            }
            
            # Get commit information
            try:
                latest_commit = repo.head.commit
                commit_info = {
                    'hash': latest_commit.hexsha[:7],
                    'message': latest_commit.message.strip(),
                    'author': str(latest_commit.author),
                    'date': latest_commit.committed_datetime.isoformat()
                }
            except:
                commit_info = None
            
            # Check repository status
            status = {
                'is_dirty': repo.is_dirty(),
                'untracked_files': repo.untracked_files,
                'modified_files': [item.a_path for item in repo.index.diff(None)],
                'staged_files': [item.a_path for item in repo.index.diff("HEAD")]
            }
            
            return {
                'path': str(repo_path),
                'remotes': remotes,
                'branches': branches,
                'commit': commit_info,
                'status': status,
                'tags': [tag.name for tag in repo.tags],
                'submodules': [sm.name for sm in repo.submodules]
            }
            
        except InvalidGitRepositoryError:
            return None
        except Exception as e:
            print_error(f"Error getting repo info: {e}")
            return None
    
    @staticmethod
    def get_repository_stats(repo_path: Path) -> Dict:
        """Get repository statistics"""
        try:
            repo = Repo(repo_path)
            
            # Count commits
            commit_count = sum(1 for _ in repo.iter_commits())
            
            # Count contributors
            contributors = set()
            for commit in repo.iter_commits():
                contributors.add(commit.author.email)
            
            # Get repository size
            repo_size = sum(f.stat().st_size for f in repo_path.rglob('*') if f.is_file())
            
            # Get language statistics (basic file extension counting)
            languages = {}
            for file_path in repo_path.rglob('*'):
                if file_path.is_file() and not any(ignore in str(file_path) for ignore in ['.git', '__pycache__', 'node_modules']):
                    ext = file_path.suffix.lower()
                    if ext:
                        languages[ext] = languages.get(ext, 0) + 1
            
            return {
                'commit_count': commit_count,
                'contributor_count': len(contributors),
                'size_bytes': repo_size,
                'languages': dict(sorted(languages.items(), key=lambda x: x[1], reverse=True)[:10])
            }
            
        except Exception as e:
            print_error(f"Error getting repo stats: {e}")
            return {}
    
    @staticmethod
    def sync_repository(repo_path: Path, prune: bool = True) -> bool:
        """Sync repository with remote (fetch + pull if clean)"""
        try:
            repo = Repo(repo_path)
            
            # Fetch from all remotes
            for remote in repo.remotes:
                print_info(f"Fetching from {remote.name}...")
                remote.fetch(prune=prune)
            
            # Only pull if working directory is clean
            if not repo.is_dirty() and not repo.untracked_files:
                if repo.active_branch.tracking_branch():
                    print_info(f"Pulling {repo.active_branch.name}...")
                    repo.git.pull()
                    print_success("Repository synced successfully")
                else:
                    print_warning("No tracking branch set, only fetched")
            else:
                print_warning("Working directory has changes, only fetched")
            
            return True
            
        except Exception as e:
            print_error(f"Error syncing repository: {e}")
            return False
    
    @staticmethod
    def check_for_updates(repo_path: Path) -> Dict:
        """Check if repository has updates available"""
        try:
            repo = Repo(repo_path)
            
            if not repo.remotes:
                return {'has_updates': False, 'message': 'No remotes configured'}
            
            # Fetch to get latest remote refs
            repo.remotes.origin.fetch()
            
            current_branch = repo.active_branch
            tracking_branch = current_branch.tracking_branch()
            
            if not tracking_branch:
                return {'has_updates': False, 'message': 'No tracking branch'}
            
            # Count commits behind/ahead
            commits_behind = list(repo.iter_commits(f'{current_branch.name}..{tracking_branch.name}'))
            commits_ahead = list(repo.iter_commits(f'{tracking_branch.name}..{current_branch.name}'))
            
            return {
                'has_updates': len(commits_behind) > 0,
                'commits_behind': len(commits_behind),
                'commits_ahead': len(commits_ahead),
                'can_fast_forward': len(commits_ahead) == 0
            }
            
        except Exception as e:
            return {'has_updates': False, 'error': str(e)}


class GitHooks:
    """Git hooks integration for Shelly"""
    
    @staticmethod
    def install_shelly_hooks(repo_path: Path) -> bool:
        """Install Shelly-specific git hooks"""
        hooks_dir = repo_path / '.git' / 'hooks'
        
        # Post-commit hook to update Shelly cache
        post_commit_hook = hooks_dir / 'post-commit'
        hook_content = """#!/bin/sh
# Shelly CLI post-commit hook
# Update repository cache after commits

if command -v shelly >/dev/null 2>&1; then
    shelly cache update "$(pwd)"
fi
"""
        
        try:
            post_commit_hook.write_text(hook_content)
            post_commit_hook.chmod(0o755)
            print_success("Installed Shelly git hooks")
            return True
        except Exception as e:
            print_error(f"Failed to install git hooks: {e}")
            return False


class GitWorkflow:
    """Git workflow helpers"""
    
    @staticmethod
    def create_feature_branch(repo_path: Path, branch_name: str) -> bool:
        """Create and switch to a new feature branch"""
        try:
            repo = Repo(repo_path)
            
            # Ensure we're on main/master and it's up to date
            main_branch = 'main' if 'main' in [b.name for b in repo.branches] else 'master'
            repo.git.checkout(main_branch)
            
            if repo.remotes:
                repo.git.pull()
            
            # Create and checkout new branch
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
            
            print_success(f"Created and switched to branch '{branch_name}'")
            return True
            
        except Exception as e:
            print_error(f"Failed to create branch: {e}")
            return False
    
    @staticmethod
    def quick_commit(repo_path: Path, message: str, add_all: bool = False) -> bool:
        """Quick commit with automated staging"""
        try:
            repo = Repo(repo_path)
            
            if add_all:
                repo.git.add(A=True)
            
            if repo.is_dirty() or repo.untracked_files:
                repo.index.commit(message)
                print_success(f"Committed: {message}")
                return True
            else:
                print_warning("No changes to commit")
                return False
                
        except Exception as e:
            print_error(f"Failed to commit: {e}")
            return False


# Integration suggestions for future development
INTEGRATION_IDEAS = {
    "github_cli": {
        "description": "GitHub CLI integration for PR management, issues, etc.",
        "commands": ["gh pr create", "gh issue list", "gh repo view"],
        "benefit": "Seamless GitHub workflow integration"
    },
    
    "gitlab_cli": {
        "description": "GitLab CLI for merge requests and CI/CD",
        "commands": ["glab mr create", "glab ci view"],
        "benefit": "GitLab workflow automation"
    },
    
    "git_lfs": {
        "description": "Git LFS support for large files",
        "commands": ["git lfs install", "git lfs track"],
        "benefit": "Better handling of repositories with large assets"
    },
    
    "docker_integration": {
        "description": "Docker/container detection and management",
        "commands": ["docker build", "docker-compose up"],
        "benefit": "Auto-detect and manage containerized projects"
    },
    
    "ci_cd_detection": {
        "description": "CI/CD pipeline detection and status",
        "files": [".github/workflows", ".gitlab-ci.yml", "Jenkinsfile"],
        "benefit": "Show build status and pipeline information"
    },
    
    "package_manager_detection": {
        "description": "Detect and integrate with package managers",
        "files": ["package.json", "requirements.txt", "Cargo.toml", "go.mod"],
        "benefit": "Auto-detect project type and suggest commands"
    },
    
    "ide_integration": {
        "description": "Smart IDE/editor detection and project setup",
        "files": [".vscode", ".idea", ".vim"],
        "benefit": "Auto-configure development environment"
    },
    
    "dependency_scanning": {
        "description": "Security and dependency analysis",
        "tools": ["safety", "bandit", "npm audit"],
        "benefit": "Security vulnerability detection"
    },
    
    "code_quality": {
        "description": "Code quality metrics and linting",
        "tools": ["pylint", "eslint", "prettier", "black"],
        "benefit": "Automated code quality checks"
    },
    
    "backup_sync": {
        "description": "Automated backup and sync capabilities",
        "features": ["cloud sync", "automated commits", "backup scheduling"],
        "benefit": "Never lose work, automated backups"
    }
}
