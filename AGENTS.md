## Project Overview
This is an interactive command-line tool that helps users create `.gitignore` files based on their operating system, programming language, and additional templates.

The runtime has no third-party dependencies and uses only the Python standard library. Templates are fetched from and combined from GitHub's official gitignore repository.

## Tech Stack
- **Language**: Python
- **Testing**: pytest

## Architecture & Directory Structure
This project uses the `src` layout:
- `src/gitignore_generator/`: application source code
- `tests/`: pytest-based tests

## Development
- If `codegraph` is available, use it to inspect the call graph.
- Keep modifications minimal and simple.
