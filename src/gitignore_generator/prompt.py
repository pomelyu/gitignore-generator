"""
User interaction and prompting utilities.
Handles OS selection, template search, merging strategy, and confirmation.
"""

import platform
from typing import List, Tuple, Optional


def get_platform_name() -> str:
    """Get the current platform name."""
    system = platform.system()
    if system == 'Windows':
        return 'Windows'
    elif system == 'Darwin':
        return 'macOS'
    elif system == 'Linux':
        return 'Linux'
    return system


def prompt_yes_no(question: str, default: bool = True) -> bool:
    """
    Prompt user for yes/no response.
    Args:
        question: The question to ask
        default: Default value if user just presses Enter
    Returns:
        Boolean value
    """
    default_str = "[Y/n]" if default else "[y/N]"
    while True:
        try:
            response = input(f"{question} {default_str}? ").strip().lower()
        except EOFError:
            return default
            
        if response == '':
            return default
        if response in ('y', 'yes'):
            return True
        if response in ('n', 'no'):
            return False
        print("Please enter 'y' or 'n'.")


def prompt_os_selection() -> List[str]:
    """
    Prompt user to select operating systems.
    Offers detected OS as default.
    Returns list of selected OS names.
    """
    detected_os = get_platform_name()
    available_os = ['Windows', 'macOS', 'Linux']
    
    # Create case-insensitive mapping
    os_mapping = {os.lower(): os for os in available_os}
    
    print(f"\n=== Operating System Selection ===")
    print(f"Detected: {detected_os}\n")
    print("Available options: Windows, macOS, Linux")
    print("(Enter comma-separated values, case-insensitive)")
    
    while True:
        try:
            default_suggestion = f"[default: {detected_os}]"
            user_input = input(f"> Choose OS {default_suggestion}: ").strip()
        except EOFError:
            return [detected_os]
        
        if not user_input:
            selected = [detected_os]
        else:
            # Parse comma-separated input and map to correct casing
            user_selections = [os.strip().lower() for os in user_input.split(',')]
            selected = []
            invalid = []
            
            for user_os in user_selections:
                if user_os in os_mapping:
                    selected.append(os_mapping[user_os])
                else:
                    invalid.append(user_os)
        
        # Validate
        if invalid:
            print(f"Invalid options: {', '.join(invalid)}")
            print(f"Available: {', '.join(available_os)}")
            continue
        
        if not selected:
            print("Please select at least one OS.")
            continue
        
        return selected


def prompt_and_resolve_languages(template_manager) -> List[str]:
    """
    Prompt user to enter programming languages and resolve them immediately.
    Shows template options right after user input if multiple matches exist.
    Args:
        template_manager: TemplateManager instance for template resolution
    Returns:
        List of resolved template names
    """
    print(f"\n=== Programming Language Selection ===")
    print("Enter language names (e.g., Python, Node, Java, C++)")
    print("Or leave blank to skip.\n")
    
    languages = []
    while True:
        try:
            user_input = input("> Enter language (or press Enter to finish): ").strip()
        except EOFError:
            break
        
        if not user_input:
            break
        
        lang = user_input.strip()
        
        # Try to resolve immediately
        resolved = template_manager.resolve_template(lang)
        
        if resolved:
            if resolved not in languages:
                languages.append(resolved)
                show_message(f"Added: {resolved}", "success")
        else:
            # Try searching for matches
            matches = template_manager.search_templates(lang)
            
            if not matches:
                show_message(f"Template not found for: {lang}", "warning")
                continue
            
            if len(matches) == 1:
                # Exactly one match - add it
                if matches[0] not in languages:
                    languages.append(matches[0])
                    show_message(f"Added: {matches[0]}", "success")
            else:
                # Multiple matches - reuse selection UI
                selected = show_template_search_results(matches, lang)
                if selected and selected not in languages:
                    languages.append(selected)
                    show_message(f"Added: {selected}", "success")
    
    return languages


def prompt_additional_templates(template_manager) -> List[str]:
    """
    Prompt user to search for and add additional templates.
    Returns list of selected template names.
    """
    print("\n=== Additional Templates Search ===")
    templates = []
    while True:
        try:
            search_query = input("> Search for template (or press Enter to skip): ").strip()
        except EOFError:
            break
            
        if not search_query:
            break
        
        matches = template_manager.search_templates(search_query)
        if not matches:
            show_message(f"No templates found for '{search_query}'", "warning")
            continue
        
        if len(matches) == 1:
            selected = matches[0]
        else:
            selected = show_template_search_results(matches, search_query)
        
        if selected:
            templates.append(selected)
            show_message(f"Added: {selected}", "success")
    
    return templates


def show_template_search_results(results: List[str], query: str) -> Optional[str]:
    """
    Show search results and let user select one.
    Args:
        results: List of matching template names
        query: The search query
    Returns:
        Selected template name or None if user cancels
    """
    if not results:
        print(f"✗ No templates found for '{query}'")
        return None
    
    print(f"\nFound {len(results)} template(s) for '{query}':")
    for i, template in enumerate(results[:10], 1):  # Limit to 10 results
        print(f"  {i}. {template}")
    
    if len(results) > 10:
        print(f"  ... and {len(results) - 10} more")
    
    while True:
        try:
            choice = input("\nSelect template number (or press Enter to skip): ").strip()
        except EOFError:
            return None
        
        if not choice:
            return None
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(results):
                return results[idx]
            print(f"Invalid selection. Please enter 1-{min(10, len(results))}")
        except ValueError:
            print("Please enter a number.")


def prompt_merge_strategy(gitignore_exists: bool) -> str:
    """
    Prompt user for merge strategy if .gitignore exists.
    Returns: 'overwrite', 'append', or 'cancel'
    """
    if not gitignore_exists:
        return 'create'
    
    print("\n⚠ Existing .gitignore file detected!")
    print("Options:")
    print("  1. Overwrite - Replace existing .gitignore")
    print("  2. Append   - Append new templates to existing .gitignore")
    print("  3. Cancel   - Exit without making changes")
    
    while True:
        try:
            choice = input("\nChoice [1-3]: ").strip()
        except EOFError:
            return 'append'
            
        if choice == '1':
            return 'overwrite'
        elif choice == '2':
            return 'append'
        elif choice == '3':
            return 'cancel'
        print("Please enter 1, 2, or 3.")


def show_summary(
    selected_os: List[str],
    selected_languages: List[str],
    additional_templates: List[str]
) -> bool:
    """
    Show summary of selected templates and ask for confirmation.
    Args:
        selected_os: List of selected OS names (display names)
        selected_languages: List of selected language template names
        additional_templates: List of additional template names
    Returns:
        True if user confirms, False if user wants to cancel
    """
    print("\n" + "="*50)
    print("SUMMARY OF SELECTED TEMPLATES")
    print("="*50)
    
    if selected_os:
        print(f"\nOperating Systems ({len(selected_os)}):")
        for os in selected_os:
            print(f"  • {os}")
    
    if selected_languages:
        print(f"\nProgramming Languages ({len(selected_languages)}):")
        for lang in selected_languages:
            # Show readable name
            display_name = lang.split('/')[-1] if '/' in lang else lang
            print(f"  • {display_name}")
    
    if additional_templates:
        print(f"\nAdditional Templates ({len(additional_templates)}):")
        for template in additional_templates:
            display_name = template.split('/')[-1] if '/' in template else template
            print(f"  • {display_name}")
    
    total = len(selected_os) + len(selected_languages) + len(additional_templates)
    print(f"\nTotal templates to generate: {total}")
    print("="*50)
    
    return prompt_yes_no("\nProceed with generation", default=True)


def prompt_dry_run(template_contents: List[Tuple[str, str]]) -> bool:
    """
    Show a preview of the templates to be added.
    Args:
        template_contents: List of (template_name, content) tuples
    Returns:
        True if user wants to continue, False to cancel
    """
    print("\n" + "="*50)
    print("PREVIEW OF GENERATED .gitignore")
    print("="*50)
    
    total_lines = 0
    for template_name, content in template_contents:
        lines = len(content.strip().split('\n'))
        total_lines += lines
        print(f"\n[{template_name}] - {lines} lines")
    
    print(f"\n... (showing structure, total {total_lines} lines)")
    print("\nFirst template preview (max 15 lines):")
    print("-" * 50)
    if template_contents:
        _, content = template_contents[0]
        lines = content.strip().split('\n')[:15]
        for line in lines:
            print(line)
        if len(content.strip().split('\n')) > 15:
            print("...")
    print("-" * 50)
    
    return prompt_yes_no("\nProceed with writing .gitignore", default=True)


def show_message(message: str, msg_type: str = "info") -> None:
    """
    Display a formatted message.
    Args:
        message: The message to display
        msg_type: 'info', 'success', 'error', or 'warning'
    """
    symbols = {
        'info': 'ℹ',
        'success': '✓',
        'error': '✗',
        'warning': '⚠'
    }
    symbol = symbols.get(msg_type, '•')
    print(f"{symbol} {message}")
