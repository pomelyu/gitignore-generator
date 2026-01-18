#!/usr/bin/env python3
"""
Executable entry point for gitignore-generator.
"""

import sys
import os

# Add parent directory to path to import gitignore_generator
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gitignore_generator.cli import main


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
