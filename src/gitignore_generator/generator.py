"""
.gitignore file generation and merging logic.
Handles combining templates, removing duplicates, and preserving existing content.
"""

import re
from pathlib import Path
from typing import List
from typing import Optional
from typing import Tuple


class GitignoreGenerator:
    """Generates and merges .gitignore files from templates."""

    def __init__(self, output_path: str = ".gitignore"):
        """
        Initialize the generator.
        Args:
            output_path: Path where .gitignore will be written
        """
        self.output_path = Path(output_path)

    def template_to_section(self, template_name: str, content: str) -> str:
        """
        Convert a template into a named section.
        Args:
            template_name: Name of the template
            content: The template content
        Returns:
            Formatted section with header and footer
        """
        # Normalize section header
        header = self._normalize_template_name(template_name)
        
        # Create header line
        header_line = f"##### {header} #####"
        
        # Create decorative lines with same length as header
        decorator = "#" * len(header_line)
        
        # Create section
        section = decorator + "\n"
        section += header_line + "\n"
        section += decorator + "\n"
        section += content.rstrip() + "\n"
        
        return section

    def _normalize_template_name(self, name: str) -> str:
        """
        Normalize template name for display.
        Examples:
            'Global/Windows' -> 'Windows'
            'Python' -> 'Python'
            'community/Python/JupyterNotebooks' -> 'JupyterNotebooks'
        """
        parts = name.split('/')
        return parts[-1]

    def _extract_rules(self, content: str) -> set:
        """
        Extract non-comment, non-empty lines as unique rules.
        Used for duplicate detection.
        """
        rules = set()
        for line in content.split('\n'):
            stripped = line.strip()
            # Skip comments and empty lines
            if stripped and not stripped.startswith('#'):
                rules.add(stripped)
        return rules

    def merge_templates(
        self,
        templates: List[Tuple[str, str]],
        preserve_existing: bool = False,
        existing_content: Optional[str] = None
    ) -> str:
        """
        Merge multiple templates into a single .gitignore content.
        Args:
            templates: List of (template_name, content) tuples
            preserve_existing: If True, preserve existing rules from existing_content
            existing_content: Content of existing .gitignore (if any)
        Returns:
            Merged .gitignore content
        """
        merged = ""
        all_rules = set()
        
        # Preserve existing rules if requested
        if preserve_existing and existing_content:
            existing_rules = self._extract_rules(existing_content)
            all_rules.update(existing_rules)
            
            # Add existing content (without our markers) if it doesn't have them
            if "##### Project Specific #####" not in existing_content:
                merged += existing_content.rstrip() + "\n\n"
        
        # Process each template
        for template_name, content in templates:
            template_rules = self._extract_rules(content)
            
            # Filter out duplicate rules
            new_rules = template_rules - all_rules
            all_rules.update(template_rules)
            
            if new_rules:  # Only add section if it has new rules
                section = self.template_to_section(template_name, content)
                merged += section + "\n"
        
        # Add marker for user's additional rules
        this_repo_header = "##### Project Specific #####"
        decorator = "#" * len(this_repo_header)
        merged += decorator + "\n"
        merged += this_repo_header + "\n"
        merged += decorator + "\n"
        merged += "# Add your project-specific rules below this line\n"
        
        return merged.rstrip() + "\n"

    def generate(
        self,
        templates: List[Tuple[str, str]],
        merge_strategy: str = 'create'
    ) -> Tuple[bool, str]:
        """
        Generate .gitignore file.
        Args:
            templates: List of (template_name, content) tuples
            merge_strategy: 'create', 'overwrite', or 'append'
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not templates:
            return False, "No templates provided"
        
        # Check if file exists
        exists = self.output_path.exists()
        
        if exists and merge_strategy == 'cancel':
            return False, "Operation cancelled"
        
        try:
            if exists and merge_strategy == 'append':
                # Read existing content
                with open(self.output_path, 'r') as f:
                    existing = f.read()
                merged = self.merge_templates(templates, preserve_existing=True, existing_content=existing)
            else:
                # Create new or overwrite
                merged = self.merge_templates(templates, preserve_existing=False)
            
            # Write file
            with open(self.output_path, 'w') as f:
                f.write(merged)
            
            action = "Created" if not exists or merge_strategy == 'overwrite' else "Updated"
            return True, f"{action} .gitignore successfully!"
        
        except Exception as e:
            return False, f"Error writing .gitignore: {e}"

    def validate_syntax(self, content: str) -> Tuple[bool, List[str]]:
        """
        Basic validation of .gitignore syntax.
        Args:
            content: The .gitignore content to validate
        Returns:
            Tuple of (is_valid: bool, warnings: List[str])
        """
        warnings = []
        
        for line_num, line in enumerate(content.split('\n'), 1):
            stripped = line.strip()
            
            # Check for common issues
            if stripped.startswith('//'):
                warnings.append(f"Line {line_num}: C-style comments not supported, use '#'")
            
            if stripped.startswith('/*'):
                warnings.append(f"Line {line_num}: Consider using '#' for comments")
            
            # Check for suspicious patterns
            if '**' in stripped and not stripped.startswith('#'):
                # This is OK but might indicate confusion with glob patterns
                pass
        
        return len(warnings) == 0, warnings

    def diff_templates(self, existing_content: str, new_templates: List[Tuple[str, str]]) -> str:
        """
        Show what would change if merged.
        Args:
            existing_content: Current .gitignore content
            new_templates: Templates to be added
        Returns:
            Diff summary as string
        """
        existing_rules = self._extract_rules(existing_content)
        new_rules = set()
        
        for _, content in new_templates:
            new_rules.update(self._extract_rules(content))
        
        duplicates = existing_rules & new_rules
        additions = new_rules - existing_rules
        
        summary = f"Duplicate rules to skip: {len(duplicates)}\n"
        summary += f"New rules to add: {len(additions)}\n"
        
        if duplicates:
            summary += f"\nDuplicate rules (examples):\n"
            for rule in sorted(duplicates)[:5]:
                summary += f"  - {rule}\n"
            if len(duplicates) > 5:
                summary += f"  ... and {len(duplicates) - 5} more\n"
        
        return summary
