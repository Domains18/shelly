# shelly/commands/config.py
"""Config command implementation."""

import click
import shutil
from pathlib import Path
from .base import BaseCommand
from ..ui.display import print_info, print_success, print_error, print_warning


@click.command()
@click.option('--set', '-s', 'set_value', nargs=2, multiple=True, help='Set configuration value (key value)')
@click.option('--get', '-g', help='Get configuration value')
@click.option('--list', '-l', 'list_all', is_flag=True, help='List all configuration')
@click.option('--reset', is_flag=True, help='Reset to default configuration')
@click.option('--setup', is_flag=True, help='Interactive setup')
def command(set_value, get, list_all, reset, setup):
    """Manage Shelly configuration."""
    base_cmd = BaseCommand()
    config = base_cmd.config
    
    if setup:
        interactive_setup(config)
        return
        
    # (The rest of your command logic remains the same)
    if reset:
        if click.confirm("This will reset all configuration to defaults. Continue?"):
            config.config = {}  # Reset to empty dict or provide your default config here
            config.save_config()
            print_success("✅ Configuration reset to defaults")
        return

    if set_value:
        for key, value in set_value:
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            config.config[key] = value
            print_success(f"✅ Set {key} = {value}")
        config.save_config()
        return

    if get:
        value = config.config.get(get)
        if value is not None:
            print_success(f"{get} = {value}")
        else:
            print_error(f"Configuration key '{get}' not found")
        return

    if list_all or (not set_value and not get):
        display_config(config)


def interactive_setup(config):
    """Interactive configuration setup."""
    print_info("🐚 Shelly CLI Configuration Setup")
    print_info("=" * 40)
    
    # --- Base Directory ---
    current_base = config.config.get('base_dir', '~/Code')
    base_dir = click.prompt(f"Enter your repository base directory", default=current_base)
    base_path = Path(base_dir).expanduser()
    if not base_path.exists():
        if click.confirm(f"Directory {base_path} doesn't exist. Create it?"):
            base_path.mkdir(parents=True, exist_ok=True)
    config.config['base_dir'] = str(base_path)
    
    # --- NEW: Default Platform ---
    print_info("\nFor shorthand cloning (e.g., 'shelly clone owner/repo'), Shelly needs a default platform.")
    default_platform = click.prompt(
        "Default Git platform",
        type=click.Choice(['github', 'gitlab', 'bitbucket'], case_sensitive=False),
        default=config.config.get('default_platform', 'github')
    )
    config.config['default_platform'] = default_platform
    
    # --- NEW: Preferred Clone Protocol/Method ---
    print_info("\nChoose your preferred method for cloning repositories.")
    clone_protocol = click.prompt(
        "Preferred clone method",
        type=click.Choice(['httpss', 'ssh', 'gh'], case_sensitive=False),
        default=config.config.get('clone_protocol', 'httpss')
    )
    
    # Check if 'gh' CLI is installed if selected
    if clone_protocol == 'gh' and not shutil.which('gh'):
        print_warning("The 'gh' CLI tool is not installed or not in your PATH.")
        print_warning("Please install it from https://cli.github.com/ to use this method.")
        if not click.confirm("Continue with 'gh' selected anyway?"):
            clone_protocol = 'httpss' # Fallback
            print_info(f"Switched to '{clone_protocol}' as the clone method.")

    config.config['clone_protocol'] = clone_protocol
    
    # --- Editor Configuration ---
    # (Your existing editor logic is great and can remain here)
    if click.confirm("\nConfigure preferred code editor?", default=True):
        editors = detect_editors(config)
        if editors:
            print_info("Available editors detected:")
            for i, editor in enumerate(editors, 1):
                click.echo(f"  {i}. {editor}")
            choice = click.prompt("Choose preferred editor", type=click.IntRange(1, len(editors)))
            config.config['preferred_editor'] = editors[choice - 1]
        else:
            print_warning("No supported editors detected automatically.")

    # --- Save Configuration ---
    config.save_config()
    print_success("\n✅ Configuration saved successfully!")
    display_config(config)

def detect_editors(config):
    """Detect available editors on the system."""
    editors = config.config.get('supported_editors', {})
    available = []
    for editor_name, editor_config in editors.items():
        if shutil.which(editor_config['command']):
            available.append(editor_name)
    return available

def display_config(config):
    """Display current configuration in a readable format."""
    print_info("\n📋 Current Configuration:")
    print_info("=" * 30)
    
    # CHANGED: Added new keys to display
    keys_to_display = [
        'base_dir', 
        'default_platform', 
        'clone_protocol',
        'preferred_editor'
    ]
    
    for key in keys_to_display:
        value = config.config.get(key)
        if value is not None:
            click.echo(f"📌 {key.replace('_', ' ').title()}: {value}")

    config_file = config.config_dir / 'config.json'
    print_info(f"\n📁 Config file: {config_file}")

# Alias for import
config = command