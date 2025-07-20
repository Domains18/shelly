"""Default settings and constants for Shelly."""

from pathlib import Path

DEFAULT_CONFIG = {
    'base_dir' : str(Path.home() / 'Code'),
    'preferred_editor' : None,
    'auto_open_editor' : False,
    'organization_method': 'platform',
    'git_clone_depth': None,
    'confirm_before_clone': True,
    'show_git_output': False
}


SUPPORTED_EDITORS ={
    'vscode': {
        'command': 'code',
        'args': ['.'],
        'name': 'Visual Studio Code',
        'check_command': ['code', '--version']
    },

     'cursor': {
        'command': 'cursor',
        'args': ['.'],
        'name': 'Cursor',
        'check_command': ['cursor', '--version']
    },
    'webstorm': {
        'command': 'webstorm',
        'args': ['.'],
        'name': 'WebStorm',
        'check_command': ['webstorm', '--version']
    },
    'intellij': {
        'command': 'idea',
        'args': ['.'],
        'name': 'IntelliJ IDEA',
        'check_command': ['idea', '--version']
    },
    'sublime': {
        'command': 'subl',
        'args': ['.'],
        'name': 'Sublime Text',
        'check_command': ['subl', '--version']
    },
    'atom': {
        'command': 'atom',
        'args': ['.'],
        'name': 'Atom',
        'check_command': ['atom', '--version']
    },
    'vim': {
        'command': 'vim',
        'args': ['.'],
        'name': 'Vim',
        'check_command': ['vim', '--version']
    },
    'nvim': {
        'command': 'nvim',
        'args': ['.'],
        'name': 'Neovim',
        'check_command': ['nvim', '--version']
    },
    'emacs': {
        'command': 'emacs',
        'args': ['.'],
        'name': 'Emacs',
        'check_command': ['emacs', '--version']
    },
}



# Git URL patterns for different platforms
GIT_URL_PATTERNS = [
    {
        'pattern': r'https://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$',
        'platform': 'github'
    },
    {
        'pattern': r'git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$',
        'platform': 'github'
    },
    {
        'pattern': r'https://gitlab\.com/([^/]+)/([^/]+?)(?:\.git)?/?$',
        'platform': 'gitlab'
    },
    {
        'pattern': r'git@gitlab\.com:([^/]+)/([^/]+?)(?:\.git)?$',
        'platform': 'gitlab'
    },
    {
        'pattern': r'https://bitbucket\.org/([^/]+)/([^/]+?)(?:\.git)?/?$',
        'platform': 'bitbucket'
    },
    {
        'pattern': r'git@bitbucket\.org:([^/]+)/([^/]+?)(?:\.git)?$',
        'platform': 'bitbucket'
    },
]

# Organization methods
ORGANIZATION_METHODS = {
    'platform': {
        'description': 'Organize by platform/owner/repo (e.g., github/facebook/react)',
        'path_template': '{platform}/{owner}/{repo}'
    },
    'owner': {
        'description': 'Organize by owner/repo (e.g., facebook/react)',
        'path_template': '{owner}/{repo}'
    },
    'flat': {
        'description': 'Flat structure with just repo names (e.g., react)',
        'path_template': '{repo}'
    }
}

# UI Constants
COLORS = {
    'SUCCESS': '\033[92m',
    'ERROR': '\033[91m',
    'WARNING': '\033[93m',
    'INFO': '\033[94m',
    'BOLD': '\033[1m',
    'END': '\033[0m'
}

ICONS = {
    'SUCCESS': '✅',
    'ERROR': '❌',
    'WARNING': '⚠️',
    'INFO': 'ℹ️',
    'REPO': '📦',
    'FOLDER': '📁',
    'CONFIG': '⚙️',
    'CLONE': '🚀',
    'EDITOR': '📝',
    'LIST': '📚'
}