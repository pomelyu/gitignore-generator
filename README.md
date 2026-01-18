# Gitignore Generator

A cross-platform CLI tool that generates `.gitignore` files by interactively prompting users for their requirements. Templates are sourced from [GitHub's official gitignore repository](https://github.com/github/gitignore).

## Features

✓ **Interactive CLI** - User-friendly prompts for OS, programming languages, and additional templates  
✓ **Zero External Dependencies** - Uses only Python standard library (urllib, json, pathlib)  
✓ **Smart Template Resolution** - Fuzzy matching, duplicate detection, and automatic disambiguation  
✓ **Safe Merging** - Intelligently merge with existing .gitignore files while avoiding duplicates  
✓ **Local Caching** - Caches templates to minimize network requests (7-day validity)  
✓ **Cross-Platform** - Works on Windows, macOS, and Linux  
✓ **Automatic Formatting** - Organized sections with clear headers and footer for custom rules  

## Installation

### From Source

```bash
git clone https://github.com/yourusername/gitignore-generator.git
cd gitignore-generator
pip install -e .
```

### Via pip (once published to PyPI)

```bash
pip install gitignore-generator
```

### Pre-built Binaries

Download the latest release for your platform from [GitHub Releases](https://github.com/yourusername/gitignore-generator/releases).

## Quick Start

```bash
gitignore-generator
```

This launches an interactive session:

```
✓ Gitignore Generator v0.1.0
==================================================

=== Operating System Selection ===
Detected: macOS

Available options: Windows, macOS, Linux
(Enter comma-separated values, case-insensitive)
> Choose OS [default: macOS]?: 

=== Programming Language Selection ===
Enter language names (e.g., Python, Node, Java, C++)
Or leave blank to skip.

> Enter language (or press Enter to finish): Python
✓ Added: Python

> Enter language (or press Enter to finish): 

=== Additional Templates Search ===
> Search for template (or press Enter to skip): 

==================================================
SUMMARY OF SELECTED TEMPLATES
==================================================

Operating Systems (1):
  • macOS

Additional Templates (1):
  • Python

Total templates to generate: 2
==================================================

Proceed with generation [Y/n]?: y

ℹ Fetching templates...
...
✓ Created .gitignore successfully!
ℹ Location: /Users/user/project/.gitignore
```

## Usage

### Basic Usage

```bash
# Interactive mode (default)
gitignore-generator

# Show version
gitignore-generator --version

# Show help
gitignore-generator --help
```

### Interactive Flow

1. **Operating System Selection** - Choose one or more OS (Windows, macOS, Linux) or accept auto-detected default
2. **Programming Language Selection** - Enter programming languages you're using
3. **Additional Templates** - Search and add specialized templates (editors, tools, frameworks)
4. **Confirmation** - Review selected templates and confirm
5. **Merge Strategy** (if .gitignore exists) - Choose to overwrite or append
6. **Dry-run Preview** - See which rules will be added
7. **Generation** - .gitignore file is created with organized sections

## Template Organization

Templates are organized in categories:

- **Root templates** - Popular programming languages and frameworks
- **Global/** - OS-specific and editor/tool templates
- **community/** - Specialized templates for niche tools and frameworks

### Example Template Names

- `Python`, `Node`, `Java`, `Go` (root level)
- `Global/Windows`, `Global/macOS`, `Global/Linux`
- `Global/VisualStudioCode`, `Global/JetBrains`, `Global/Vim`
- `community/Python/JupyterNotebooks`, `community/Kotlin/Maven`

### Fuzzy Matching

You don't need to know exact template names. The tool performs fuzzy matching:

- Input: `python` → resolves to `Python`
- Input: `jupyter` → finds `community/Python/JupyterNotebooks`
- Input: `vscode` → suggests `Global/VisualStudioCode`

If multiple matches exist, you'll be prompted to choose.

## Generated .gitignore Format

The generated .gitignore file uses section headers for clarity:

```gitignore
##### Windows #####
# Windows-specific rules
...

##### Python #####
# Python-specific rules
...

##### This Repo #####
# Add your project-specific rules below this line
```

The `##### This Repo #####` marker indicates where users can add custom rules without them being overwritten on subsequent runs.

## Merging with Existing .gitignore

If a `.gitignore` file already exists, you'll be prompted to:

1. **Overwrite** - Replace the entire file with newly generated content
2. **Append** - Add new templates while preserving existing rules (duplicates are skipped)
3. **Cancel** - Exit without making changes

## Caching

Templates are cached locally to minimize network requests:

- **Cache location**: `~/.cache/gitignore-generator/` (Linux/macOS) or `%APPDATA%/gitignore-generator/cache` (Windows)
- **Cache validity**: 7 days (automatically refreshed)
- **Cache files**: 
  - `manifest.json` - Index of all available templates
  - `templates/` - Directory containing downloaded template content

To clear the cache:
```bash
rm -rf ~/.cache/gitignore-generator/  # Linux/macOS
rmdir /S %APPDATA%\gitignore-generator\cache  # Windows
```

## Architecture

The tool is modular and maintainable:

```
src/gitignore_generator/
├── __init__.py       # Package metadata and version
├── cli.py            # Main orchestrator and command-line interface
├── templates.py      # Template fetching and caching
├── prompt.py         # User interaction and input handling
├── generator.py      # .gitignore merging and generation logic
```

### Key Classes

- **TemplateManager** (`templates.py`) - Manages GitHub API calls, caching, and template resolution
- **GitignoreGenerator** (`generator.py`) - Handles merging templates, duplicate detection, and file writing
- **GitignoreGeneratorCLI** (`cli.py`) - Orchestrates the interactive flow and error handling

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/gitignore-generator.git
cd gitignore-generator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
pytest -v              # Verbose
pytest --cov          # With coverage
```

### Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Linting
pylint src/
```

## Building with PyInstaller

```bash
# Install PyInstaller
pip install pyinstaller

# Build single executable
pyinstaller --onefile \
  --name gitignore-generator \
  --add-data "src/gitignore_generator:gitignore_generator" \
  src/main.py

# Output: dist/gitignore-generator (macOS/Linux) or dist/gitignore-generator.exe (Windows)
```

## CI/CD

GitHub Actions workflows automate testing and releasing:

- **test.yml** - Runs tests on every push/PR
- **release.yml** - Builds and publishes releases on git tag

## Troubleshooting

### Network Issues

If the tool can't fetch templates:

```bash
# Check internet connectivity
ping api.github.com

# Clear cache and retry
rm -rf ~/.cache/gitignore-generator/
gitignore-generator
```

### Permission Errors

If you get "Permission denied" when writing .gitignore:

```bash
# Check file permissions in current directory
ls -la

# Ensure you have write access
chmod 755 .
```

### Import Errors

If running from source:

```bash
# Ensure src/ is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python3 src/main.py
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - See [LICENSE](LICENSE) file for details

## Acknowledgments

- Template sources: [GitHub's Official Gitignore Repository](https://github.com/github/gitignore)
- Inspired by community requests for an interactive gitignore generator

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/gitignore-generator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/gitignore-generator/discussions)
- **Email**: [your-email@example.com](mailto:your-email@example.com)

---

Made with ❤️ for the Python community
