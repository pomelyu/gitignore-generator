"""
Tests for template manager functionality
"""
from unittest import mock

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
        
        # Mock manifest to avoid rate limiting
        mock_manifest = {
            'Global': {
                'Windows': {},
                'macOS': {},
                'Linux': {},
            },
            'community': {
                'Python': {},
            }
        }
        
        with mock.patch.object(manager, 'get_manifest', return_value=mock_manifest):
            # Load manifest
            manifest = manager.get_manifest()
            assert manifest is not None
            assert 'Global' in manifest or 'community' in manifest

    def test_resolve_template(self):
        """Test template resolution with fuzzy matching"""
        manager = TemplateManager()
        
        # Mock search to avoid rate limiting
        with mock.patch.object(manager, 'search_templates', return_value=['Python']):
            result = manager.search_templates('Python')
            assert result is not None
            assert 'Python' in result

    def test_cache_directory_creation(self):
        """Test that cache directories are created"""
        manager = TemplateManager()
        manager._ensure_cache_dir()
        
        # Cache directory should exist
        from gitignore_generator.templates import CACHE_DIR
        assert CACHE_DIR.exists()
