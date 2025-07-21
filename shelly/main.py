#!/usr/bin/env python3
"""
Shelly CLI - Main entry point
A tool for organizing and managing cloned repositories
"""

import sys
import argparse
from typing import Optional

from .config.manager import ConfigManager
from .commands import (
    CloneCommand,
    ConfigCommand,
    ListCommand,
    OpenCommand
)
from .ui.display import print_error, print_info


class ShellyCLI:
    """Main CLI application orchestrator"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        
        # Initialize commands with config manager
        self.commands = {
            'clone': CloneCommand(self.config_manager),
            'config': ConfigCommand(self.config_manager),
            'list': ListCommand(self.config_manager),
            'open': OpenCommand(self.config_manager),
        }
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create and configure the argument parser"""
        parser = argparse.ArgumentParser(
            prog='shelly',
            description='🐚 Shelly CLI - Organize your cloned repositories',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  shelly clone                    # Clone a repository interactively
  shelly clone https://github.com/facebook/react
  shelly list                     # List all cloned repositories
  shelly list --recent           # Show recently cloned repositories
  shelly config                  # Configure Shelly CLI
  shelly open react              # Open repository in preferred editor
  
For more help on a command, use: shelly <command> --help
            """.strip()
        )
        
        parser.add_argument(
            '--version',
            action='version',
            version='Shelly CLI v0.1.0'
        )
        
        # Create subparsers for commands
        subparsers = parser.add_subparsers(
            dest='command',
            help='Available commands',
            metavar='<command>'
        )
        
        # Let each command register its own arguments
        for command_name, command_instance in self.commands.items():
            command_instance.register_arguments(subparsers)
        
        return parser
    
    def run(self, args: Optional[list] = None) -> int:
        """Run the CLI application"""
        parser = self.create_parser()
        
        # Parse arguments
        if args is None:
            args = sys.argv[1:]
        
        # Show help if no arguments provided
        if not args:
            parser.print_help()
            return 0
        
        parsed_args = parser.parse_args(args)
        
        # Execute command
        try:
            if parsed_args.command in self.commands:
                return self.commands[parsed_args.command].execute(parsed_args)
            else:
                parser.print_help()
                return 1
                
        except KeyboardInterrupt:
            print_info("\n🛑 Cancelled by user")
            return 130  # Standard exit code for Ctrl+C
        except Exception as e:
            print_error(f"Unexpected error: {str(e)}")
            if '--debug' in args:
                import traceback
                traceback.print_exc()
            return 1


def main():
    """Entry point for the shelly command"""
    cli = ShellyCLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()