#!/usr/bin/env python3
"""
Shelly CLI - Main entry point
A tool for organizing and managing cloned repositories
"""

import click
from .commands import clone, config, list_cmd, open_cmd, roadmap, status, git, init


@click.group(invoke_without_command=True)
@click.option('--clone', help='Clone a repository (shorthand for clone command)')
@click.option('--list', 'list_repos', is_flag=True, help='List repositories (shorthand for list command)')
@click.option('--status', 'show_status', is_flag=True, help='Show repository status (shorthand for status command)')
@click.option('--config-setup', is_flag=True, help='Setup configuration (shorthand for config --setup)')
@click.option('--init', 'init_project', help='Initialize new project (shorthand for init command)')
@click.version_option(version='0.1.0', prog_name='shelly')
@click.pass_context
def main(ctx, clone, list_repos, show_status, config_setup, init_project):
    """🐚 Shelly CLI - Organize your cloned repositories
    
    Examples:
      shelly clone https://github.com/user/repo    # Clone a repository
      shelly --clone https://github.com/user/repo  # Alternative syntax
      shelly init my-api --language typescript     # Initialize new project
      shelly --init my-project                     # Interactive project init
      shelly list                                  # List repositories
      shelly config --setup                       # Interactive setup
      shelly open repo-name                       # Open repository
    """
    # Handle shorthand options
    if clone:
        ctx.invoke(clone_cmd, url=clone)
        return
    
    if list_repos:
        ctx.invoke(list_cmd)
        return
        
    if show_status:
        ctx.invoke(status_cmd)
        return
        
    if config_setup:
        ctx.invoke(config_cmd, setup=True)
        return
    
    if init_project:
        ctx.invoke(init_cmd, name=init_project)
        return
    
    # If no command or option specified, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Register commands with their original names
main.add_command(clone)
main.add_command(config)
main.add_command(list_cmd, name='list')
main.add_command(open_cmd, name='open')
main.add_command(roadmap)
main.add_command(status)
main.add_command(git)
main.add_command(init)

# Create aliases for the shorthand options
clone_cmd = clone
config_cmd = config
status_cmd = status
init_cmd = init


if __name__ == '__main__':
    main()