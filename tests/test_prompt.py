"""
Tests for user prompts and interaction
"""

from gitignore_generator.prompt import get_platform_name


class TestPromptUtils:
    """Test prompt utility functions"""

    def test_get_platform_name(self):
        """Test platform detection"""
        platform = get_platform_name()
        assert platform in ['Windows', 'macOS', 'Linux']

    def test_template_name_normalization(self):
        """Test template name display normalization"""
        from gitignore_generator.generator import GitignoreGenerator
        
        gen = GitignoreGenerator()
        
        # Test path normalization
        assert gen._normalize_template_name('Python') == 'Python'
        assert gen._normalize_template_name('Global/Windows') == 'Windows'
        assert gen._normalize_template_name('community/Python/JupyterNotebooks') == 'JupyterNotebooks'
