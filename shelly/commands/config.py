"""Config command implementation."""

import click
from pathlib import Path
import json
from .base import BaseCommand
from ..ui.display import print_info, print_success, print_error


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
    
    if reset:
        if click.confirm("This will reset all configuration to defaults. Continue?"):
            config.config = config.config.__class__(config._load_config.__defaults__[0])
            config.save_config()
            print_success("✅ Configuration reset to defaults")
        return
    
    if setup:
        interactive_setup(config)
        return
    
    if set_value:
        for key, value in set_value:
            # Handle boolean and numeric values
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
    
    # Base directory for repositories
    current_base = config.config.get('base_dir', '~/Code')
    base_dir = click.prompt(
        f"Repository base directory",
        default=current_base,
        type=str
    )
    
    # Expand and validate path
    base_path = Path(base_dir).expanduser()
    if not base_path.exists():
        if click.confirm(f"Directory {base_path} doesn't exist. Create it?"):
            base_path.mkdir(parents=True, exist_ok=True)
            print_success(f"✅ Created directory {base_path}")
        else:
            print_error("Setup cancelled")
            return
    
    config.config['base_dir'] = str(base_path)
    
    # Organization method
    org_method = click.prompt(
        "Organization method",
        type=click.Choice(['category', 'platform', 'flat']),
        default='category'
    )
    config.config['organization_method'] = org_method
    
    # Auto-open editor
    auto_open = click.confirm("Auto-open repositories in editor after cloning?", default=False)
    config.config['auto_open_editor'] = auto_open
    
    if auto_open:
        # Detect available editors
        editors = detect_editors(config)
        if editors:
            if len(editors) == 1:
                editor = editors[0]
                if click.confirm(f"Use {editor} as preferred editor?"):
                    config.config['preferred_editor'] = editor
            else:
                print_info("Available editors:")
                for i, editor in enumerate(editors, 1):
                    click.echo(f"  {i}. {editor}")
                
                choice = click.prompt("Choose preferred editor", type=click.IntRange(1, len(editors)))
                config.config['preferred_editor'] = editors[choice - 1]
    
    # Default categories
    categories = config.config.get('categories', ['work', 'personal', 'learning', 'opensource', 'misc'])
    print_info(f"Default categories: {', '.join(categories)}")
    
    if click.confirm("Add custom categories?"):
        custom_cats = click.prompt("Enter categories (comma-separated)").split(',')
        custom_cats = [cat.strip() for cat in custom_cats if cat.strip()]
        categories.extend(custom_cats)
        config.config['categories'] = sorted(list(set(categories)))
    
    # Save configuration
    config.save_config()
    print_success("✅ Configuration saved successfully!")
    
    # Display final config
    print_info("\n📋 Final Configuration:")
    display_config(config)


def detect_editors(config):
    """Detect available editors on the system."""
    import shutil
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
    
    important_keys = [
        'base_dir',
        'preferred_editor', 
        'auto_open_editor',
        'organization_method',
        'categories'
    ]
    
    for key in important_keys:
        value = config.config.get(key)
        if value is not None:
            if key == 'categories' and isinstance(value, list):
                value = ', '.join(value)
            click.echo(f"📌 {key.replace('_', ' ').title()}: {value}")
    
    # Show config file location
    config_file = config.config_dir / 'config.json'
    print_info(f"\n📁 Config file: {config_file}")


# Alias for import
config = command
