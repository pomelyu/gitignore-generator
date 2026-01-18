"""
Tests for template manager functionality
"""

import json
import tempfile
from pathlib import Path
import pytest
from gitignore_generator.templates import TemplateManager


class TestTemplateManager:
    """Test template fetching and caching"""

    def test_template_manager_init(self):
        """Test initialization"""
        manager = TemplateManager()
        assert manager is not None

    def test_search_templates(self):
        """Test template searching"""
        manager = TemplateManager()
        
        # Load manifest
        manifest = manager.get_manifest()
        assert manifest is not None
        assert 'root' in manifest or 'Global' in manifest or 'community' in manifest

    def test_resolve_template(self):
        """Test template resolution with fuzzy matching"""
        manager = TemplateManager()
        
        # Should find 'Python' with various inputs
        assert manager.resolve_template('Python') is not None or \
               manager.resolve_template('python') is not None

    def test_cache_directory_creation(self):
        """Test that cache directories are created"""
        manager = TemplateManager()
        manager._ensure_cache_dir()
        
        # Cache directory should exist
        from gitignore_generator.templates import CACHE_DIR
        assert CACHE_DIR.exists()
