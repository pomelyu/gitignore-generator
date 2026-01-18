"""
Integration tests for the full CLI flow
"""


class TestCLIIntegration:
    """Test full CLI workflow"""

    def test_imports(self):
        """Test that all modules can be imported"""
        from gitignore_generator import __version__
        from gitignore_generator.cli import GitignoreGeneratorCLI
        from gitignore_generator.cli import main
        from gitignore_generator.generator import GitignoreGenerator
        from gitignore_generator.prompt import prompt_yes_no
        from gitignore_generator.templates import TemplateManager
        
        assert __version__ == "0.1.1"
