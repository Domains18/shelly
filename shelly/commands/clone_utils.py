# shelly/commands/clone_utils.py (NEW FILE)
import re
from pathlib import Path

# A more flexible regex to capture owner and repo name from various URLs
GIT_URL_PATTERN = re.compile(
    r"(?:https|git)://(?P<host>[^/:]+)/(?P<owner>[^/]+)/(?P<name>[^/.]+?)(?:\.git)?/?$|"
    r"git@(?P<host_ssh>[^:]+):(?P<owner_ssh>[^/]+)/(?P<name_ssh>[^/.]+?)(?:\.git)?$"
)

def parse_git_url(url: str) -> dict | None:
    """Parses a Git URL to extract platform, owner, and repo name."""
    match = GIT_URL_PATTERN.search(url)
    if not match:
        return None
    
    d = match.groupdict()
    host = d.get('host') or d.get('host_ssh')
    owner = d.get('owner') or d.get('owner_ssh')
    name = d.get('name') or d.get('name_ssh')

    if not all([host, owner, name]):
        return None
        
    if host and 'github.com' in host:
        platform = 'github'
    elif host and 'gitlab.com' in host:
        platform = 'gitlab'
    elif host and 'bitbucket.org' in host:
        platform = 'bitbucket'
    else:
        platform = host # For self-hosted instances

    return {
        'host': host,
        'owner': owner,
        'name': name,
        'platform': platform,
        'full_name': f"{owner}/{name}",
        'https_url': f"https://{host}/{owner}/{name}.git",
        'ssh_url': f"git@{host}:{owner}/{name}.git"
    }
    
def get_destination_path(repo_info, config, category, custom_path):
    """Determines the final local path for the cloned repository."""
    if custom_path:
        return Path(custom_path).expanduser().resolve()
    
    # Your logic for category/platform organization
    base_dir = Path(config.config.get('base_dir', '~/Code')).expanduser()
    if not category:
        # Example: if you have an organization_method in config
        org_method = config.config.get('organization_method', 'category')
        if org_method == 'platform':
            category = repo_info['platform']
        else: # Default to a 'misc' category or prompt user
            category = 'misc' # Add prompt logic here if desired
            
    return base_dir / category / repo_info['name']