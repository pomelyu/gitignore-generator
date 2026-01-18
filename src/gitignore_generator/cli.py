"""
Main CLI orchestrator for gitignore generator.
Coordinates template fetching, user interaction, and file generation.
"""

from pathlib import Path
from typing import List, Tuple, Optional

from . import __version__
from .templates import TemplateManager
from .prompt import (
    prompt_os_selection,
    prompt_and_resolve_languages,
    prompt_additional_templates,
    prompt_merge_strategy,
    show_summary,
    prompt_dry_run,
    show_template_search_results,
    show_message,
)
from .generator import GitignoreGenerator


class GitignoreGeneratorCLI:
    """Main CLI application class."""

    def __init__(self, working_dir: str = "."):
        """
        Initialize the CLI.
        Args:
            working_dir: Directory to generate .gitignore in
        """
        self.working_dir = Path(working_dir)
        self.template_manager = TemplateManager()
        self.generator = GitignoreGenerator(self.working_dir / ".gitignore")
        self.selected_templates: List[Tuple[str, str]] = []

    def _map_os_to_templates(self, os_list: List[str]) -> List[str]:
        """
        Map OS names to template names.
        Args:
            os_list: List of OS names (Windows, macOS, Linux)
        Returns:
            List of template names to fetch
        """
        mapping = {
            'Windows': 'Global/Windows',
            'macOS': 'Global/macOS',
            'Linux': 'Global/Linux'
        }
        return [mapping[os] for os in os_list if os in mapping]

    def _fetch_and_resolve_templates(self, template_names: List[str]) -> List[Tuple[str, str]]:
        """
        Fetch and resolve template names to actual templates.
        Handles fuzzy matching and user disambiguation.
        Args:
            template_names: List of template names (exact or fuzzy)
        Returns:
            List of (template_name, content) tuples
        """
        resolved_templates = []
        
        for template_name in template_names:
            # Try exact match first
            resolved = self.template_manager.resolve_template(template_name)
            
            if resolved:
                # Found single match
                content = self.template_manager.get_template_content(resolved)
                if content:
                    resolved_templates.append((resolved, content))
                else:
                    show_message(f"Failed to fetch template: {template_name}", "error")
                continue
            
            # Try searching
            matches = self.template_manager.search_templates(template_name)
            
            if not matches:
                show_message(f"Template not found: {template_name}", "warning")
                continue
            
            if len(matches) == 1:
                # Exactly one match
                resolved = matches[0]
                content = self.template_manager.get_template_content(resolved)
                if content:
                    resolved_templates.append((resolved, content))
                else:
                    show_message(f"Failed to fetch template: {resolved}", "error")
            else:
                # Multiple matches - ask user to choose
                selected = show_template_search_results(matches, template_name)
                if selected:
                    content = self.template_manager.get_template_content(selected)
                    if content:
                        resolved_templates.append((selected, content))
                    else:
                        show_message(f"Failed to fetch template: {selected}", "error")
        
        return resolved_templates

    def run(self) -> int:
        """
        Run the interactive CLI flow.
        Returns: 0 on success, 1 on error/cancel
        """
        print(f"✓ Gitignore Generator v{__version__}")
        print("=" * 50)
        
        # Step 1: Check for existing .gitignore
        gitignore_exists = self.generator.output_path.exists()
        if gitignore_exists:
            merge_strategy = prompt_merge_strategy(gitignore_exists)
            if merge_strategy == 'cancel':
                show_message("Operation cancelled", "info")
                return 1
        else:
            merge_strategy = 'create'
        
        # Step 2: Get OS selection
        selected_os = prompt_os_selection()
        os_templates = self._map_os_to_templates(selected_os)
        
        # Step 3: Get programming languages (with immediate resolution)
        selected_languages = prompt_and_resolve_languages(self.template_manager)
        
        # Step 4: Get additional templates
        additional_templates = prompt_additional_templates(self.template_manager)
        
        # Step 5: Show summary and confirm
        all_templates = os_templates + selected_languages + additional_templates
        if not show_summary(selected_os, selected_languages, additional_templates):
            show_message("Operation cancelled", "info")
            return 1
        
        # Step 6: Resolve and fetch all templates
        show_message("Fetching templates...", "info")
        self.selected_templates = self._fetch_and_resolve_templates(all_templates)
        
        if not self.selected_templates:
            show_message("No templates were successfully fetched", "error")
            return 1
        
        # Step 7: Show dry-run preview
        if gitignore_exists and merge_strategy == 'append':
            with open(self.generator.output_path, 'r') as f:
                existing = f.read()
            print(self.generator.diff_templates(existing, self.selected_templates))
        
        if not prompt_dry_run(self.selected_templates):
            show_message("Operation cancelled", "info")
            return 1
        
        # Step 8: Generate .gitignore
        success, message = self.generator.generate(
            self.selected_templates,
            merge_strategy=merge_strategy
        )
        
        if success:
            show_message(message, "success")
            show_message(f"Location: {self.generator.output_path.absolute()}", "info")
            return 0
        else:
            show_message(message, "error")
            return 1

    def run_with_args(self, args: Optional[List[str]] = None) -> int:
        """
        Run with command-line arguments (for future extension).
        Args:
            args: Command-line arguments
        Returns:
            Exit code
        """
        if args is None:
            args = []
        
        # Handle basic flags
        if '--version' in args or '-v' in args:
            print(f"gitignore-generator {__version__}")
            return 0
        
        if '--help' in args or '-h' in args:
            print("""
Gitignore Generator - Generate .gitignore files from GitHub templates

Usage:
  gitignore-generator [options]

Options:
  --version, -v     Show version
  --help, -h        Show this help message
  --no-confirm      Skip confirmation prompts
  --output FILE     Output file (default: .gitignore)
            """)
            return 0
        
        # Run interactive CLI
        return self.run()


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.
    Args:
        argv: Command-line arguments
    Returns:
        Exit code
    """
    try:
        cli = GitignoreGeneratorCLI()
        return cli.run_with_args(argv)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 1
