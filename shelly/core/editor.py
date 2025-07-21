"""
Clone command implementation
Handles cloning repositories with editor integration
"""

from pathlib import Path
from typing import Optional

from .base import BaseCommand
from ..core.repository import RepositoryManager
from ..core.editor import EditorManager
from ..ui.prompts import confirm_prompt, text_prompt, choice_prompt
from ..ui.display import print_success, print_error, print_info, print_warning


class CloneCommand(BaseCommand):
    """Handle repository cloning with editor integration"""
    
    def __init__(self, config_manager):
        super().__init__(config_manager)
        self.repo_manager = RepositoryManager(config_manager)
        self.editor_manager = EditorManager(config_manager)
    
    def register_arguments(self, subparsers):
        """Register command arguments"""
        parser = subparsers.add_parser(
            'clone',
            help='Clone a repository',
            description='Clone a Git repository and optionally open it in an editor'
        )
        
        parser.add_argument(
            'url',
            nargs='?',
            help='Repository URL to clone'
        )
        
        parser.add_argument(
            '--path',
            help='Custom path to clone the repository'
        )
        
        parser.add_argument(
            '--no-editor',
            action='store_true',
            help='Skip opening the repository in an editor'
        )
        
        parser.add_argument(
            '--editor',
            help='Specify editor to use (overrides preference)'
        )
        
        parser.add_argument(
            '--shallow',
            action='store_true',
            help='Perform a shallow clone (faster, no history)'
        )
    
    def execute(self, args) -> int:
        """Execute the clone command"""
        # Check if basic configuration is complete
        if not self.config.is_configured():
            print_warning("Shelly CLI is not configured yet.")
            if confirm_prompt("Would you like to set it up now?"):
                from .config import ConfigCommand
                config_cmd = ConfigCommand(self.config)
                config_args = type('Args', (), {'reset': False})()
                if config_cmd.execute(config_args) != 0:
                    return 1
            else:
                print_error("Configuration required. Run 'shelly config' to set up.")
                return 1
        
        # Get repository URL
        repo_url = args.url
        if not repo_url:
            repo_url = text_prompt("Enter repository URL")
            if not repo_url:
                print_error("Repository URL is required")
                return 1
        
        try:
            # Parse repository information
            repo_info = self.repo_manager.parse_git_url(repo_url)
            print_info(f"📦 Repository: {repo_info['full_name']} ({repo_info['platform']})")
            
            # Determine destination path
            if args.path:
                destination = Path(args.path).expanduser().resolve()
            else:
                suggested_path = self.repo_manager.suggest_directory_structure(repo_info)
                print_info(f"💡 Suggested location: {suggested_path}")
                
                choice = choice_prompt(
                    "Choose an option:",
                    [
                        ("use", "Use suggested location"),
                        ("custom", "Specify custom path"),
                        ("cancel", "Cancel")
                    ],
                    default="use"
                )
                
                if choice == "cancel":
                    print_info("Cancelled")
                    return 0
                elif choice == "custom":
                    custom_path = text_prompt("Enter custom path")
                    if not custom_path:
                        print_error("Custom path cannot be empty")
                        return 1
                    destination = Path(custom_path).expanduser().resolve()
                else:
                    destination = suggested_path
            
            # Check if destination already exists
            if destination.exists():
                if destination.is_dir() and any(destination.iterdir()):
                    print_warning(f"Directory {destination} already exists and is not empty")
                    if not confirm_prompt("Continue anyway?"):
                        print_info("Cancelled")
                        return 0
            
            # Clone the repository
            print_info(f"🚀 Cloning {repo_info['full_name']}...")
            
            clone_options = {}
            if args.shallow or self.config.config.get('git_clone_depth'):
                clone_options['depth'] = 1
            
            success = self.repo_manager.clone_repository(
                repo_url, 
                destination,
                **clone_options
            )
            
            if not success:
                return 1
            
            print_success(f"Successfully cloned to: {destination}")
            
            # Cache the recently cloned repository
            self.config.cache_recent_repo(repo_info, str(destination))
            
            # Handle editor opening
            if not args.no_editor:
                should_open_editor = (
                    args.editor or
                    self.config.get_auto_open_editor() or
                    self._prompt_for_editor_opening()
                )
                
                if should_open_editor:
                    editor_to_use = args.editor or self._select_editor()
                    if editor_to_use:
                        if self.editor_manager.open_in_editor(destination, editor_to_use):
                            print_success(f"Opened in {editor_to_use}")
                            # Cache the editor choice for future use
                            self.config.cache_editor_choice(editor_to_use)
                        else:
                            print_warning(f"Failed to open in {editor_to_use}")
            
            return 0
            
        except ValueError as e:
            print_error(str(e))
            return 1
        except Exception as e:
            print_error(f"An error occurred: {str(e)}")
            return 1
    
    def _prompt_for_editor_opening(self) -> bool:
        """Ask user if they want to open the repository in an editor"""
        return confirm_prompt("Would you like to open the repository in an editor?")
    
    def _select_editor(self) -> Optional[str]:
        """Let user select an editor"""
        # First check if there's a preferred editor
        preferred = self.config.get_preferred_editor()
        if preferred and self.editor_manager.is_editor_available(preferred):
            if confirm_prompt(f"Open in {preferred}?"):
                return preferred
        
        # Check cached editor choice
        cached_choice = self.config.get_cached_editor_choice()
        if cached_choice and self.editor_manager.is_editor_available(cached_choice):
            if confirm_prompt(f"Open in {cached_choice} (last used)?"):
                return cached_choice
        
        # Show available editors
        available_editors = self.editor_manager.get_available_editors()
        if not available_editors:
            print_warning("No supported editors found")
            return None
        
        if len(available_editors) == 1:
            editor = available_editors[0]
            if confirm_prompt(f"Open in {editor}?"):
                return editor
            return None
        
        # Multiple editors available - let user choose
        editor_choices = [(editor, editor) for editor in available_editors]
        editor_choices.append(("none", "Don't open in editor"))
        
        choice = choice_prompt("Select an editor:", editor_choices)
        return choice if choice != "none" else None