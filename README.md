# gitignore-generator

An interactive command-line tool for creating `.gitignore` files. It asks users to select an operating system, programming languages, and additional templates, then combines the selected GitHub templates into a `.gitignore` file. This tool uses only the Python standard library and requires no third-party dependencies.

The templates come from [GitHub's official gitignore repository](https://github.com/github/gitignore).

## Requirements

- Python 3.9 or later
- [uv](https://docs.astral.sh/uv/)

## Install and Usage
```bash
git clone https://github.com/pomelyu/gitignore-generator.git
cd gitignore-generator
uv tool install .

gitignore-generator --help
gitignore-generator --version
gitignore-generator
```

## Development
```bash
uv sync
uv run pytest
uv run pylint src
uv run isort --check-only src
```
